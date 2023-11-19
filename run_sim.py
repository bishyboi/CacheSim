
import seaborn as sns
from subprocess import Popen, PIPE, STDOUT
import pandas as pd
import matplotlib.pyplot as plt

global CACHE_MIN
CACHE_MIN = 10

global CACHE_MAX
CACHE_MAX = 15

global LINE_SIZE
LINE_SIZE = 6

global FILENAME
FILENAME = "trace_files/swim.trace"

global lru_cmd
lru_cmd = "./cache_sim_LRU".split()

global fifo_cmd
fifo_cmd = "./cache_sim_FIFO".split()


def generate_input_message(cache_size: int, line_size: int, cache_implementation: int, filename: str) -> str:
    """
    Returns the input string for the cache_sim based on the cache size, line size, and cache implementation
    For cache_implementation: 
    0: fully associative,
    1: direct mapped,
    2: 2-way,
    3: 4-way,
    4: 8-way,
    5: 16-way
    """
    messages = [str(cache_size), str(line_size)]

    if cache_implementation == 0:
        messages.append("y")
    elif cache_implementation == 1:
        messages.append("n")
        messages.append("y")
    else:
        messages.append("n")
        messages.append("n")
        messages.append(str(cache_implementation-1))

    messages.append(filename)

    write_message = ""

    for message in messages:
        write_message += f"{message}\n"

    return write_message


def get_output(command: list[int], input_message: str) -> str:
    """Takes the input parameters in the form of a string and runs a subprocess, returning the output

    Args:
        command (list[int]): a command converted to a list of arguments that are put into the process
        input_message (str): process inputs, defined by generate_input_message()

    Returns:
        str: _description_
    """
    p = Popen(command, stdout=PIPE, stdin=PIPE, stderr=STDOUT, text=True)

    response = p.communicate(input=input_message)

    final_msg = response[0]
    p.terminate()

    return final_msg


def get_hit_rate(output_msg) -> float:
    """Parses the hit rate from a get_output message

    Args:
        output_msg (str): return value of get_output()

    Returns:
        float: A value between 0 and 1 that is the hit rate from the input parameters
    """
    hit_output = output_msg.find("hit rate ")
    offset = len("hit rate ")
    hit_rate = float(output_msg[hit_output+offset:])

    return hit_rate


def calc_implementation(data: pd.DataFrame, cache_implementation: str):
    """Will add the hit rate entries for the cache implementation type onto the DataFrame

    Args:
        data (pandas.DataFrame): a DataFrame with columns "Hit Rate", "Cache Implementation", and "Cache Size"
        cache_implementation (str): Specified Cache Implementation Type
    """
    global CACHE_MAX
    global CACHE_MIN
    global FILENAME
    global lru_cmd
    global fifo_cmd

    cache_no = 0
    lru = ("FIFO" not in cache_implementation)
    cmd = lru_cmd if lru else fifo_cmd

    if "Fully Associative" in cache_implementation:
        cache_no = 0
    elif "Direct Mapped" in cache_implementation:
        cache_no = 1
    elif "2-Way Set Associative" in cache_implementation:
        cache_no = 2
    elif "4-Way Set Associative" in cache_implementation:
        cache_no = 3
    elif "8-Way Set Associative" in cache_implementation:
        cache_no = 4
    else:
        cache_no = 5

    for cache_size in range(CACHE_MIN, CACHE_MAX):
        input_message = generate_input_message(
            cache_size, LINE_SIZE, cache_no, FILENAME)
        output_msg = get_output(cmd, input_message)
        row = {
            "Hit Rate": get_hit_rate(output_msg),
            "Cache Implementation": cache_implementation,
            "Cache Size": 2**cache_size
        }

        data.loc[len(data)] = row


def main():

    cache_implementations = ["Direct Mapped",
                             "Fully Associative (LRU)",
                             "2-Way Set Associative (LRU)",
                             "4-Way Set Associative (LRU)",
                             "8-Way Set Associative (LRU)",
                             "Fully Associative (FIFO)",
                             "2-Way Set Associative (FIFO)",
                             "4-Way Set Associative (FIFO)",
                             "8-Way Set Associative (FIFO)"]

    data = pd.DataFrame(
        columns=["Hit Rate", "Cache Implementation", "Cache Size"])

    # Goes through each implementation type and calculates the hit rates for each cache size
    for implementation in cache_implementations:
        calc_implementation(data, implementation)

    # Saving hit rate data into a .CSV file
    data.to_csv("HitRates.csv")

    # ** Plotting details
    plt.figure(figsize=(16, 9))
    sns.set_theme()

    # Set plot title and labels
    plt.title('Analysis of Cache Implementations: Cache Size vs. Hit Rate')
    plt.xlabel('Cache Size (Bytes)')
    plt.ylabel('Hit Rates (Accuracy)')

    sns.lineplot(data=data, x="Cache Size", y="Hit Rate",
                 hue="Cache Implementation", palette="husl")

    # # Save the plot to a file (e.g., PNG, PDF, SVG))
    plt.savefig('CacheAnalysis.png', dpi=400)
    plt.savefig('CacheAnalysis.svg')
    plt.savefig('CacheAnalysis.pdf')

    # Show the plot (optional)
    plt.show()


if __name__ == "__main__":
    main()
