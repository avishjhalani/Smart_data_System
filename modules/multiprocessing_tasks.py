from multiprocessing import Process

def run_in_process(func, *args):
    p = Process(target=func, args=args)
    p.start()
    return p


def generate_plots_in_process(processor_cls, df):
    """
    Worker entrypoint for multiprocessing.

    We construct the processor inside the worker to reduce pickling issues with bound methods.
    """
    processor = processor_cls()
    processor.generate_plots(df)