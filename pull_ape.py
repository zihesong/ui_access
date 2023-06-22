import subprocess
import re
import os
import shutil
import glob

def grep_apk_files(folder_path):
    apk_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.apk'):
                apk_files.append(os.path.join(root, file))

    return apk_files


def get_package_name(apk_file_path):
    try:
        # Run the aapt command to get the package name
        output = subprocess.check_output(['aapt', 'dump', 'badging', apk_file_path]).decode('utf-8')

        # Use regular expressions to extract the package name from the output
        package_name_match = re.search(r"package: name='([^']+)'.*", output)
        if package_name_match:
            return package_name_match.group(1)
        else:
            print("Failed to extract package name from APK file.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing aapt command: {e}")
        return None


def run_ape(package_name, running_time):
    command = f"adb shell CLASSPATH=/data/local/tmp/ape.jar /system/bin/app_process /data/local/tmp/ com.android.commands.monkey.Monkey -p {package_name} --running-minutes {running_time} --ape sata"
    
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")


def pull_result_file(output_path, package_name, running_time):
    result_file_path = f"/sdcard/sata-{package_name}-ape-sata-running-minutes-{running_time}"
    os.makedirs(output_path, exist_ok=True)

    try:
        subprocess.run(["adb", "pull", result_file_path, output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while pulling the result file: {e}")


def copy_unique_screens(output_path, input_path, package_name, running_time):
    result_file_path = f"{input_path}/sata-{package_name}-ape-sata-running-minutes-{running_time}"
    result_folder = f"{output_path}/{package_name}"
    os.makedirs(result_folder, exist_ok=True)

    txt_files = glob.glob(f"{result_file_path}/step-*.txt")
    for txt_file in txt_files:
        txt_file_name = os.path.basename(txt_file)
        number = txt_file_name.split("-")[1]

        xml_file = f"{result_file_path}/step-{number}.xml"
        png_file = f"{result_file_path}/step-{number}.png"

        if os.path.exists(xml_file) and os.path.exists(png_file):
            shutil.copy2(xml_file, result_folder)
            shutil.copy2(png_file, result_folder)


if __name__ == '__main__':
    app_folder_path = "path_to_app_folder"
    ape_result_path = "path_to_save_ape_results"
    screen_path = "path_to_save_screenshots_and_xml_files"
    running_time = 1

    apk_files = grep_apk_files(app_folder_path)
    for apk_file in apk_files:
        package_name = get_package_name(apk_file)
        if package_name:
            run_ape(package_name, running_time)
            pull_result_file(ape_result_path, package_name, running_time)
            copy_unique_screens(screen_path, ape_result_path, package_name, running_time)