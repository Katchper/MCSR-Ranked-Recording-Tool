import argparse



def check_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--autostart",
        action="store_true",
    )

    args = parser.parse_args()

    if args.autostart:
        return True

    return False
