# %%
# Run #

import argparse
import sys


# %%
# Run #


def main(input_value):
    # Your script's logic here
    print("Input value:", input_value)


# %%
# Run #

if __name__ == "__main__":
    if "ipykernel" in sys.argv[0]:
        print("Running in IPython kernel")
        default_input = "default_value"
        main(default_input)
    else:
        parser = argparse.ArgumentParser(description="Your script description")
        parser.add_argument("-i", "--input", type=str, help="Input value")

        args = parser.parse_args()

        if args.input:
            main(args.input)
        else:
            default_input = "default_value"
            main(default_input)


# %%
