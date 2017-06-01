import pandas as pd
import glob
from sys import argv
import os


def memstats(file, outfile=None):
    memagg = pd.read_csv(file,
                         delimiter='|',
                         header=1,
                         skipfooter=True,
                         skiprows=0)

    memagg = memagg.drop(["Unnamed: 0", "Unnamed: 5"], axis=1)
    memagg.columns = [c.strip().replace(" ", "-") for c in memagg.columns]

    std_df = pd.DataFrame(memagg.std()).transpose()
    std_df.columns = [c + "-std" for c in std_df.columns]

    mean_df = pd.DataFrame(memagg.mean()).transpose()
    mean_df.columns = [c + "-mean" for c in mean_df.columns]

    stats = pd.concat([mean_df, std_df], axis=1)

    if outfile:
        stats.to_csv(outfile, index=False, index_label=False)
    else:
        return stats


def runtime(file, outfile=None):
    runtimes = pd.read_csv(file, header=None)

    mean_df = pd.DataFrame(runtimes.mean()).transpose()
    mean_df.columns = ["mean"]
    std_df = pd.DataFrame(runtimes.std()).transpose()
    std_df.columns = ["std"]

    stats = pd.concat([mean_df, std_df], axis=1)

    if outfile:
        stats.to_csv(outfile, index=False, index_label=False)
    else:
        return stats


if __name__ == "__main__":

    results = []

    for directory in glob.glob("*"):
        print(directory)
        if not os.path.isdir(directory):
            continue
        try: 
            _, size, locality, mode = directory.split(".")
        except ValueError:
            _, size, mode = directory.split(".")
            locality = 'local'

        row = {
            'mode':mode,
            'locality': locality,
            'size': size
        }

        os.chdir(directory)
        results_f = glob.glob("*.results")[0]
        print(results_f)
        mem_f = glob.glob("*.aggregate")[0]
        print(mem_f)
        memagg = memstats(mem_f)
        timeagg = runtime(results_f)
        row['rss-mean'] = memagg["RSS-(GB)-mean"].values[0]
        row['rss-std'] = memagg["RSS-(GB)-std"].values[0]
        row['time-mean'] = timeagg['mean'].values[0]
        row['time-std'] = timeagg['std'].values[0]
        os.chdir("..")
        results.append(row)

    everything = pd.DataFrame(results)
    print(everything)
    everything.to_csv("all_results.csv")
