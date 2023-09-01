from utils import schedule_in_multiple_factory, pretty_print, plot


INF = int(1e+14)
jobs = [
    [[  7, 10, 11],
     [  2,  8,INF]],
    [[  7,  6, 10],
     [  9,  9,  7],
     [ 12,  7, 13]],
    [[ 17,INF,  9],
     [ 14, 10,INF],
     [ 10,  6,  5]]
]
n_machines = 3
n_factories = 2

operation_genome = [2,2,1,0,1,0,1,2]
factory_genome   = [0,0,0,1,0,1,0,0]

makespan, schedules = \
schedule_in_multiple_factory(operation_genome,
                             factory_genome,
                             jobs, n_machines, n_factories)


# visualization
pretty_print(schedules)
plot(schedules, len(jobs), n_machines, n_factories,
     target="example.svg",
     seed=813)
