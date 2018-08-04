import multiprocessing, queue, time

class Worker(multiprocessing.Process):

    def __init__(self, work_queue):
        # base class initialization
        multiprocessing.Process.__init__(self)

        # job management stuff
        self.work_queue = work_queue
        self.kill_received = False

    def run(self):

        while not self.kill_received:

            # get a task
            try:
                n_job, data = self.work_queue.get_nowait()
            except Queue.Empty:
                break

            # the actual processing
            print("Starting %d ..." % n_job)
            print(str(data))
            time.sleep(10)


if __name__ == "__main__":

    data1 = 'bob'
    data2 = 'joe'

    work_queue = multiprocessing.Queue()
    for n, data in enumerate([data1, data2]):
        work_queue.put( (n, data) )

    num_processes = 2
    for i in range(num_processes):
        worker = Worker(work_queue)
        worker.start()