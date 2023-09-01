"""
Useful utilities for distributed assembly flexible job shop scheduling
Written by Yifan He (heyif@outlook.com)
Last updated on Aug. 25, 2023
"""
from random import randint
from random import seed as rseed
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def makespan(schedules):
    finish_times = []
    for schedule in schedules:
        if len(schedule) == 0:
            finish_times.append(0)
        else:
            finish_times.append(schedule[-1][-1])
    return max(finish_times)


def insert_operation_to_schedule(time_of_operation,
                                 job_of_operation,
                                 finish_time_of_previous_operation,
                                 schedule):
    """
    insert an operation into a schedule of a machine
    e.g., an operation with time cost 7
          a machine with schedule [(1,1,3), (2,6,9), (1,20,22)]
              (each tuple in the list shows job, start, and end of an operation)
          the new schedule after insertion should be as follows.
              [(1,1,3), (2,6,9), (3,9,16), (1,20,22)]
    """
    if len(schedule) == 0:
        return [(job_of_operation,
                 finish_time_of_previous_operation,
                 finish_time_of_previous_operation+time_of_operation)]

    insert_before_last_operation = False
    schedule_ = [(None,0,0)] + schedule # dummy schedule for convenience
    for index, (slot1,slot2) in enumerate(zip(schedule_, schedule)):
        start_of_idle = slot1[-1]
        end_of_idle = slot2[1]
        if end_of_idle > finish_time_of_previous_operation:
            start = max(finish_time_of_previous_operation, start_of_idle)
            # insert operation into idle slot if possible
            if end_of_idle - start >= time_of_operation:
                slot_of_operation = (job_of_operation,
                                     start,
                                     start+time_of_operation)
                return schedule[:index] + [slot_of_operation] + schedule[index:]

    if not insert_before_last_operation:
        # insert operation after last operation
        start_of_idle = schedule[-1][-1]
        start = max(finish_time_of_previous_operation, start_of_idle)
        slot_of_operation = (job_of_operation,
                             start,
                             start+time_of_operation)
        return schedule + [slot_of_operation]


def finish_time_of_last_operation(job, schedules):
    """
    compute finish time of last operation of a given job
    """
    max_end = 0
    for schedule_in_machine in schedules:
        for j, _, end in schedule_in_machine:
            if j == job:
                if end > max_end:
                    max_end = end
    return max_end


def schedule_in_single_factory(genome, jobs, n_machines):
    """
    generate schedules in single factory
    """
    n_jobs = len(jobs)
    operation_counter = [0 for _ in range(n_jobs)]
    machine_schedules = [[] for _ in range(n_machines)]

    for gene in genome:
        # get operation from genome
        operation = jobs[gene][operation_counter[gene]]
        finish_time = finish_time_of_last_operation(gene, machine_schedules)

        # allocate machine for operation to minimize current makespan
        best_makespan = None
        best_machine = None
        best_schedule = None
        for machine, time_of_operation in enumerate(operation):
            schedule = insert_operation_to_schedule(time_of_operation,
                                                    gene,
                                                    finish_time,
                                                    machine_schedules[machine])
            tmp_makespan = makespan([schedule]+ machine_schedules)
            if best_makespan == None or best_makespan > tmp_makespan:
                best_makespan = tmp_makespan
                best_machine = machine
                best_schedule = schedule
        machine_schedules[best_machine] = best_schedule

        operation_counter[gene] += 1

    return machine_schedules


def schedule_in_multiple_factory(operation_genome,
                                 factory_genome,
                                 jobs,
                                 n_machines,
                                 n_factories):
    # genome for each factory
    subgenomes = [[] for _ in range(n_factories)]
    for op, fac in zip(operation_genome, factory_genome):
        subgenomes[fac].append(op)

    # schedules in multiple factories
    schedules = []
    for subgenome in subgenomes:
        schedules.append(schedule_in_single_factory(subgenome,
                                                    jobs,
                                                    n_machines))

    tmp = []
    for schedule_in_factory in schedules:
        for schedule in schedule_in_factory:
            tmp.append(schedule)

    return makespan(tmp), schedules


def pretty_print(schedules):
    for i, schedule_in_factory in enumerate(schedules):
        print(f"factory {i}")
        for j, schedule_in_machine in enumerate(schedule_in_factory):
            print(f"  machine {j}: ", end="")
            for slot in schedule_in_machine:
                print(slot, end=" ")
            print()


def plot(schedules,
         n_jobs,
         n_machines,
         n_factories,
         colors=None,
         target=None,
         figsize=(6.4,4.8),
         subplots_adjust=(0.1,0.1,0.85,0.9,0.2,0.2),
         barwidth=0.6,
         seed=None):
    """
    plot gantt chart of a given schedule

    target: None->plt.show() | "example.png"->save to png
    figsize: set the figure size of the plot ( see plt.figure(figsize=(_,_)) )
    subplots_adjust: set subplots placement ( see plt.subplots_adjust() )
    """
    if seed:
        rseed(seed)

    # generate random but different colors if not specified
    if colors == None:
        random_number = randint(0, 16**6-1)
        random_numbers = [random_number]
        colors = [dec2color(random_number)]
        while len(colors) < n_jobs:
            diff = 0
            while diff < 16*6-1/(n_jobs*3):
                random_number = randint(0, 16**6-1)
                diffs = [abs(i-random_number) for i in random_numbers]
                diff = sum(diffs) / len(random_numbers)
            color_string = dec2color(random_number)
            if color_string not in colors:
                colors.append(color_string)

    # add subplots and placement
    fig, ax = plt.subplots(n_factories, 1, figsize=figsize)
    plt.subplots_adjust(*subplots_adjust)

    max_end = 0
    for i, schedule in enumerate(schedules):
        for m, machine in enumerate(schedule):
            for job, start, end in machine:
                # add rectangle for a slot in schedule
                ax[i].add_patch(Rectangle((start,m),
                                          end-start,
                                          barwidth,
                                          ec="black",
                                          fc=colors[job]))
                if max_end < end:
                    max_end = end # update makespan

        # yifan's aesthetic
        ax[i].set_ylim(-barwidth/2,n_machines)
        ax[i].set_xlim(0,max_end+1)
        ax[i].set_yticks([k+barwidth/2 for k in range(n_machines)],
                            [f"M{k}" for k in range(n_machines)])
        ax[i].set_ylabel(f"Factory {i}")
        ax[i].spines[["right", "top"]].set_visible(False)
    ax[-1].set_xlabel("Time")
    fig.suptitle(f"Makespan = {max_end}")

    # legend
    fig.legend(
        [Rectangle((0,0),1,1,
                   ec="black",
                   fc=colors[i]) for i in range(n_jobs)],
        range(n_jobs),
        title="Jobs",
        frameon=False
    )

    # save plot to target or show directly
    if target:
        plt.savefig(target)
    else:
        plt.show()


def dec2color(dec):
    """
    convert decimal number to hex color string
    """
    color_string = str(hex(dec))[2:]
    color_string = "#"+"0"*(6-len(color_string))+color_string
    return color_string
