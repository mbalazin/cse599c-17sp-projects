import pprint
pp = pprint.PrettyPrinter(indent=2)
answers = {}
percent_errors = {}

workload_type = 'skewed_big'
query_ids = ['0', '1', '2', '3', '4']
sampling_types = ['BERNOULLI', 'SYSTEM']
sampling_percentages = ['0.1', '1', '5', '10']
run_ids = ['run-1', 'run-2', 'run-3', 'run-4', 'run-5']

def initialize():
    for query_id in query_ids:
        query_answer_dict = {}
        query_answer_dict['exact'] = []
        for st in sampling_types:
            st_dict = {}
            for sp in sampling_percentages:
                run_answers_dict = {}
                for run_id in run_ids:
                    run_answers_dict[run_id] = []
                st_dict[sp] = run_answers_dict
            query_answer_dict[st] = st_dict
        answers[query_id]  = query_answer_dict

def get_answers_file(query_id, run_id):
    file_name = run_id + '/'
    file_name += 'results_' + workload_type + '_' + query_id + '.txt'
    return file_name

def parse_aggregate_line(line):
    answers = []
    cols = line.split(',')
    for col in cols:
        if col.strip():
            answer = float(col)
            answers.append(answer)
    return answers

def parse_aggregate_section(file):
    line = file.readline()
    return parse_aggregate_line(line)

def parse_aggregate_group_by_section(file):
    line = file.readline()
    answers = []
    while line is not None and line.strip():
        answer = parse_aggregate_line(line)
        if len(answer) > 0:
            answers.append(answer)
        line = file.readline()
    return answers

def load_answers():
    for query_id in query_ids:
        # read the exact answers first
        with open(get_answers_file(query_id, 'exact')) as answers_file:
            if query_id == '0' or query_id == '1' or query_id == '4':
                answers[query_id]['exact'] = parse_aggregate_section(answers_file)
            else:
                answers[query_id]['exact'] = parse_aggregate_group_by_section(answers_file)

        # read answers for reach run
        for run_id in run_ids:
            with open(get_answers_file(query_id, run_id)) as answers_file:
                for st in sampling_types:
                    for sp in sampling_percentages:
                        if query_id == '0' or query_id == '1' or query_id == '4':
                            answers[query_id][st][sp][run_id] = parse_aggregate_section(answers_file)
                        else:
                            answers[query_id][st][sp][run_id] = parse_aggregate_group_by_section(answers_file)

def compute_average_errors():
    for query_id in query_ids:
        percent_errors[query_id] = {}
        for st in sampling_types:
            percent_errors[query_id][st] = {}
            for sp in sampling_percentages:
                if query_id == '0' or query_id == '1' or query_id == '4':
                    exact_answer = answers[query_id]['exact']
                    average_precent_error = [0.0, 0.0, 0.0]
                    for run_id in run_ids:
                        answer = answers[query_id][st][sp][run_id]
                        for i in range(0, len(answer)):
                            if i != 2:
                                estimate   = answer[i] *  100.0 / float(sp)
                            else :
                                estimate = answer[i]
                            error = abs(estimate - exact_answer[i])
                            percent_error = error/exact_answer[i] * 100
                            average_precent_error[i] = average_precent_error[i] +  percent_error
                    for i in range(0, len(average_precent_error)):
                        average_precent_error[i] = average_precent_error[i]/5.0;                        
                    percent_errors[query_id][st][sp] = average_precent_error
                else:
                    exact_answer = answers[query_id]['exact']
                    # creating structure to store percent errors
                    average_precent_error = {}
                    for i in range(0, len(exact_answer)):
                        group_id = exact_answer[i][0]
                        average_precent_error[group_id] = [0.0, 0.0, 0.0]
                    # computing average percent error
                    for run_id in run_ids:
                        answer = answers[query_id][st][sp][run_id]
                        for i in range(0, len(answer)):
                            # for each group, just look at the aggregates
                            for j in range(1, len(answer[i])):
                                group_id = answer[i][0]
                                if j != 3:
                                    estimate = answer[i][j] *  100.0 / float(sp)
                                else :
                                    estimate = answer[i][j]
                                error = abs(estimate - exact_answer[i][j])
                                percent_error = error/exact_answer[i][j] * 100
                                average_precent_error[group_id][j-1] = average_precent_error[group_id][j-1] +  percent_error
                    for i in range(0, len(exact_answer)):
                        group_id = exact_answer[i][0]
                        for j in range(0, len(average_precent_error[group_id])):
                            average_precent_error[group_id][j] = average_precent_error[group_id][j]/5.0;                        
                    percent_errors[query_id][st][sp] = average_precent_error


def print_analysis_results():
    for query_id in query_ids:
        print "Query " + query_id
        for st in sampling_types:
            for sp in sampling_percentages:
                if query_id == '0' or query_id == '1' or query_id == '4':
                    errors = percent_errors[query_id][st][sp]
                    print_str = st + ", " + sp + ", " 
                    print_str = print_str +  str(errors[0]) + ", "
                    print_str = print_str +  str(errors[1]) + ", "
                    print_str = print_str +  str(errors[2])
                    print print_str
                else:
                    dict_errors = percent_errors[query_id][st][sp]
                    for group_id in dict_errors:
                        errors = dict_errors[group_id]
                        print_str = st + ", " + sp + ", " + str(group_id) + ", "
                        print_str = print_str +  str(errors[0]) + ", "
                        print_str = print_str +  str(errors[1]) + ", "
                        print_str = print_str +  str(errors[2])
                        print print_str
initialize()
load_answers()
compute_average_errors()
print_analysis_results()
#pp.pprint(percent_errors)
