# %%
# Running Imports #


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import paramiko
from utils.display_tools import pprint_df

# %%
# Running Imports #


# Function to execute a command remotely over SSH
def run_ssh_command(ssh_client, command):
    print(f"Running {command} on {ssh_client.get_transport().getpeername()[0]}")
    stdin, stdout, stderr = ssh_client.exec_command(command)
    return stdout.read().decode()


def run_sysbench(ssh_client, cpu_max_prime):
    num_cores_command = "nproc"
    num_cores_result = run_ssh_command(ssh_client, num_cores_command)
    num_cores = int(num_cores_result.strip())

    command = f"sysbench cpu --cpu-max-prime={cpu_max_prime} --threads={num_cores} run | grep 'total number of events:' | awk '{{print $5}}'"
    result = run_ssh_command(ssh_client, command)
    print(f"Sysbench result: {result}")

    result = float(result.replace("s", "").strip())
    return result


def get_cpu_temperature(ssh_client):
    try:
        command = "cat /sys/class/thermal/thermal_zone0/temp"
        temperature_output = run_ssh_command(ssh_client, command)
        temperature_celsius = int(temperature_output.strip()) / 1000
    except Exception:
        temperature_celsius = np.nan
    return temperature_celsius


def get_cpu_name(ssh_client):
    try:
        command = "lscpu | grep 'Model name' | awk '{print $3, $4, $5, $6, $7, $8}'"
        cpu_name = run_ssh_command(ssh_client, command).strip()
    except Exception:
        cpu_name = "Unknown"
    return cpu_name


def get_cpu_cores_threads(ssh_client):
    try:
        command = "grep -c '^processor' /proc/cpuinfo"
        cpu_cores = int(run_ssh_command(ssh_client, command))

        command = "grep -c '^siblings' /proc/cpuinfo"
        cpu_threads = int(run_ssh_command(ssh_client, command))
        if cpu_threads == 0:
            cpu_threads = cpu_cores

        return cpu_cores, cpu_threads
    except Exception:
        return None, None


def graph_results(df_results):
    # graph sysbench and temperature with bar graph for each host
    fig, ax = plt.subplots(2, 1, figsize=(15, 10))
    ax[0].bar(df_results["hostname"], df_results["sysbench_num_events"])
    ax[0].set_title("Sysbench Number of Events")

    ax[1].bar(df_results["hostname"], df_results["cpu_temp_celcius"])
    ax[1].set_title("CPU Temperature (Celsius)")
    plt.show()


def get_systems_test_results(ls_ssh_clients, cpu_max_prime):
    df_results = pd.DataFrame(
        columns=[
            "hostname",
            "cores",
            "threads",
            "cpu_name",
            "sysbench_num_events",
            "cpu_temp_celcius",
        ]
    )
    for system in ls_ssh_clients:
        print(f" {'#'*40} Running {system['hostname']} {'#'*40}")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(
                system["hostname"],
                username=system["username"],
            )

            cpu_cores, cpu_threads = get_cpu_cores_threads(ssh_client)
            cpu_name = get_cpu_name(ssh_client)
            sysbench_result = run_sysbench(ssh_client, cpu_max_prime)
            cpu_temp = get_cpu_temperature(ssh_client)

            ssh_client.close()
        except Exception as e:
            print(f"Failed for host {system['hostname']} because of: {e}")

            cpu_cores = np.nan
            cpu_threads = np.nan
            cpu_name = np.nan
            sysbench_result = np.nan
            cpu_temp = np.nan

        df_new_row = pd.DataFrame(
            {
                "hostname": system["hostname"],
                "cores": cpu_cores,
                "threads": cpu_threads,
                "cpu_name": cpu_name,
                "sysbench_num_events": sysbench_result,
                "cpu_temp_celcius": cpu_temp,
            },
            index=[0],
        )
        pprint_df(df_new_row)
        df_results = pd.concat([df_results, df_new_row], ignore_index=True)

    return df_results


# %%
# Running Imports #

if __name__ == "__main__":
    systems = [
        {
            "hostname": "EliteDesk",
            "username": "jason",
        },
        {
            "hostname": "Optiplex9020",
            "username": "jason",
        },
        {
            "hostname": "Pavilioni5",
            "username": "jason",
        },
        {
            "hostname": "Pavilioni7",
            "username": "jason",
        },
        {
            "hostname": "raspberrypi0",
            "username": "pi",
        },
        {
            "hostname": "raspberrypi3",
            "username": "pi",
        },
        {
            "hostname": "raspberrypi3a",
            "username": "pi",
        },
        {
            "hostname": "raspberrypi4",
            "username": "pi",
        },
        {
            "hostname": "raspberrypi4a",
            "username": "pi",
        },
        {
            "hostname": "HelloFreshJason",
            "username": "jason",
        },
    ]

    df_results = get_systems_test_results(systems, cpu_max_prime=20000)
    pprint_df(df_results)
    graph_results(df_results)


# %%
