# Copy iRacing setups files to the specific car.

import argparse
import os
import shutil
import re
import os
import json
import sys
import zipfile

ACTUAL_USER = os.getlogin()
FILES_END_WITH = ".sto"

def loadConfig(args):
    config_path = os.path.join(getScriptDirectory(), "config.json")
    if args.debug:
        print("Loading configuration from: ", config_path)
    return loadJson(config_path)

def loadCarsToDirectoryPathsVrs(args):
    vrsjson = os.path.join(getScriptDirectory(), "supplier", "vrs.json")
    if args.debug:
        print("Loading VRS car mappings from: ", vrsjson)
    return loadJson(vrsjson)

def loadCarsToDirectoryPathsP1Doks(args):
    p1doksjson = os.path.join(getScriptDirectory(), "supplier", "p1doks.json")
    if args.debug:
        print("Loading P1Doks car mappings from: ", p1doksjson)
    return loadJson(p1doksjson)

def loadCarsToDirectoryPathsGo(args):
    gojson = os.path.join(getScriptDirectory(), "supplier", "go.json")
    if args.debug:
        print("Loading GO car mappings from: ", gojson)
    return loadJson(gojson)

def getScriptDirectory():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def loadJson(path):
    with open(path, "r", encoding="utf-8") as f:
        # Return a dict
        return json.load(f)

def padWeekNr(args, text: str) -> str:
    if args.debug:
        print("Week for padding: ", text)
    match = re.match(r"W(\d+)", text)
    if match:
        num = int(match.group(1))
        return f"W{num:02d}"
    return text

# p1doks
def p1doks(args, source_dir, target_dir_prefix, target_dir_suffix):
    # Load the directory names
    PathsToCars = loadCarsToDirectoryPathsP1Doks(args)

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        if not os.path.isfile(file_path):
            continue
            
        FILES_START_WITH = "P1Doks"
        if not filename.lower().startswith(FILES_START_WITH.lower()):
            continue

        if not filename.lower().endswith(FILES_END_WITH.lower()):
            continue

        # Split filename and extension
        name, ext = os.path.splitext(filename)
        if args.debug:
            print("Setup : " + filename)

        parts = name.split("_")

        target_dir_car = PathsToCars[parts[1]]
        weekPattern = r"W\d+"
        if len(parts) >= 6:
            week = parts[5]
            if args.debug:
                print("Season and Week: ", week)
                print("Week after cutting: ", re.search(weekPattern, week).group())
            target_dir_seasonAndWeek = parts[5][0:4] + padWeekNr(args, re.search(weekPattern, week).group())
        else:
            week = parts[4]
            if args.debug:
                print("Season and Week: ", week)
                print("Week after cutting: ", re.search(weekPattern, week).group())
            target_dir_seasonAndWeek = parts[4][0:4] + padWeekNr(args, re.search(weekPattern, week).group())
        if args.debug:
            print("Week after padding: ", target_dir_seasonAndWeek)

        # Build target path
        target_dir = target_dir_prefix + target_dir_car + target_dir_suffix + target_dir_seasonAndWeek
        copyOrMoveFiles(args, target_dir, file_path, filename)

# GO
def buildGoTargetDir(args, filename, PathsToCars, target_dir_prefix, target_dir_suffix):
    name = os.path.splitext(os.path.basename(filename))[0].upper()
    target_dir_car = None
    for car_key in sorted(PathsToCars.keys(), key=len, reverse=True):
        if car_key.upper() in name:
            target_dir_car = PathsToCars[car_key]
            break

    if target_dir_car is None:
        raise ValueError(f"No GO car mapping found in filename: {filename}")

    target_dir_seasonAndWeek = ""
    season_week_match = re.search(r"(?P<year>\d{2})S(?P<week>\d+)", name)
    if season_week_match:
        target_dir_seasonAndWeek = f"20{season_week_match.group('year')}W{int(season_week_match.group('week')):02d}"
    else:
        week_match = re.search(r"(?P<year>(?:19|20)\d{2})W(?P<week>\d+)", name)
        if week_match:
            target_dir_seasonAndWeek = f"{week_match.group('year')}W{int(week_match.group('week')):02d}"
        else:
            week_match = re.search(r"W(?P<week>\d+)", name)
            if week_match:
                target_dir_seasonAndWeek = f"W{int(week_match.group('week')):02d}"

    if args.debug:
        print("Car mapping: ", target_dir_car)
        print("Week after padding: ", target_dir_seasonAndWeek)
    target_dir = os.path.join(target_dir_prefix, target_dir_car, target_dir_suffix, target_dir_seasonAndWeek)
    return target_dir

def moveGoZipSetups(args, zip_path, PathsToCars, target_dir_prefix, target_dir_suffix):
    zip_name = os.path.splitext(os.path.basename(zip_path))[0]
    extract_dir = os.path.join(os.path.dirname(zip_path), zip_name + "_extracted")

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

    with zipfile.ZipFile(zip_path, "r") as archive:
        archive.extractall(extract_dir)

    extracted_files = []
    for root, _, files in os.walk(extract_dir):
        for file_name in files:
            if file_name.lower().endswith(FILES_END_WITH.lower()):
                extracted_files.append(os.path.join(root, file_name))

    for file_path in sorted(extracted_files):
        filename = os.path.basename(file_path)
        target_dir = buildGoTargetDir(args, zip_path, PathsToCars, target_dir_prefix, target_dir_suffix)
        copyOrMoveFiles(args, target_dir, file_path, filename)

    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)

def go(args, source_dir, target_dir_prefix, target_dir_suffix):
    # GO uses the same setup naming pattern as P1Doks in most cases.
    PathsToCars = loadCarsToDirectoryPathsGo(args)

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        if not os.path.isfile(file_path):
            continue

        if filename.lower().startswith("go") and filename.lower().endswith(".zip"):
            moveGoZipSetups(args, file_path, PathsToCars, target_dir_prefix, target_dir_suffix)
            continue

        FILES_START_WITH = "GO"
        if not filename.lower().startswith(FILES_START_WITH.lower()):
            continue

        if not filename.lower().endswith(FILES_END_WITH.lower()):
            continue

        if args.debug:
            print("Setup : " + filename)

        target_dir = buildGoTargetDir(args, filename, PathsToCars, target_dir_prefix, target_dir_suffix)
        copyOrMoveFiles(args, target_dir, file_path, filename)

# VRS
def vrs(args, source_dir, target_dir_prefix, target_dir_suffix):
    weekInput = input("Which week? 1,2,...11,12 or even 13?: ").strip()
    week = "W"+weekInput
    # Load the directory names into a dict
    PathsToCars = loadCarsToDirectoryPathsVrs(args)

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        if not os.path.isfile(file_path):
            continue
            
        FILES_START_WITH = "VRS"
        if not filename.lower().startswith(FILES_START_WITH.lower()):
            continue

        if not filename.lower().endswith(FILES_END_WITH.lower()):
            continue

        # Split filename and extension        
        name, ext = os.path.splitext(filename)
        if args.debug:
            print("Starting working on setup : " + filename)

        if '_' in name:
            parts = name.split("_")
            if args.debug:
                print("Split successful")
        elif ' ' in name:
            parts = name.split(" ")
            if args.debug:
                print("Split successful")
        else:
            raise ValueError('Error in split!')
        
        for part in parts:
            if PathsToCars.get(part) is not None:
                target_dir_car = PathsToCars.get(part)
                break
        
        while target_dir_car is None:
            car_abbrv_dict_index = car_abbrv_dict_index + 1
            if car_abbrv_dict_index+1 > len(parts):
                print("Error: abbreviation for setup " + filename + " not found in list. Please add it!")
                return
            car_abbrv = parts[car_abbrv_dict_index]
            target_dir_car = PathsToCars.get(car_abbrv)

        if args.debug:
            print("Car abbreviation: " + car_abbrv)
            print("Directory for abbreviation: " + target_dir_car)

        # Remove the abbreviation appended to the season.
        season = parts[1][0:4]
        target_dir_seasonAndWeek = season+padWeekNr(args, week)
        if args.debug:
            print("Week after padding: ", target_dir_seasonAndWeek)

        # Build target path
        target_dir = target_dir_prefix + target_dir_car + target_dir_suffix + target_dir_seasonAndWeek
        copyOrMoveFiles(args, target_dir, file_path, filename)

def copyOrMoveFiles(args, target_dir, file_path, filename):
    target_folder = os.path.join(target_dir)

    os.makedirs(target_folder, exist_ok=True)

    # Copy or move file
    if not args.dryrun:
        if args.sandbox:
            shutil.copy(file_path, os.path.join(target_folder, filename))
            print(f"→ {filename} copied to {target_folder}")
        else:
            shutil.move(file_path, os.path.join(target_folder, filename))
            print(f"→ {filename} moved to {target_folder}")
    else:
        print(f"→ {filename} should go to {target_folder}")

def main():

    # Argumentparser
    parser = argparse.ArgumentParser(description="Beispielskript mit Parametern")

    # Add parameter
    parser.add_argument("--debug", action="store_true",
                        help="Show debug output and move files to sandbox.")
    parser.add_argument("--sandbox", action="store_true",
                        help="Copy to sandbox instead of iRacing.")
    parser.add_argument("--dryrun", action="store_true",
                        help="Does everything except copying or moving files.")

    # Parse parameter
    args = parser.parse_args()

    # Sourcedirectory
    config = loadConfig(args)
    src_dir = config.get("srcdir").replace("DUMMY_USER", ACTUAL_USER)


    # Targetdirectory
    if args.sandbox:
        target_dir_prefix = config.get("sandbox").replace("DUMMY_USER", ACTUAL_USER)
    else:
        target_dir_prefix = config.get("irsetupdir").replace("DUMMY_USER", ACTUAL_USER)
    if args.debug:
        print("Target directory: "+target_dir_prefix)

    target_dir_team = config.get("subdir")
    target_dir_supplier_p1 = "P1Doks"
    target_dir_supplier_vrs = "VRS"
    target_dir_supplier_go = "GO"

    # Choose setup provider
    choice = input("Which setup provider? (VRS 1 - P1Doks 2 - GO 3): ").strip()

    try:
        target_dir_suffix_wo_sup = os.path.join(target_dir_team)
        if choice == "1":
            target_dir_suffix = os.path.join(target_dir_suffix_wo_sup, target_dir_supplier_vrs, '')
            if args.debug:
                print("Target Team + Setup Provider: "+target_dir_suffix)
            vrs(args, src_dir, target_dir_prefix, target_dir_suffix)
        elif choice == "2":
            target_dir_suffix = os.path.join(target_dir_suffix_wo_sup, target_dir_supplier_p1, '')
            if args.debug:
                print("Target Team + Setup Provider: "+target_dir_suffix)
            p1doks(args, src_dir, target_dir_prefix, target_dir_suffix)
        elif choice == "3":
            target_dir_suffix = os.path.join(target_dir_suffix_wo_sup, target_dir_supplier_go, '')
            if args.debug:
                print("Target Team + Setup Provider: "+target_dir_suffix)
            go(args, src_dir, target_dir_prefix, target_dir_suffix)
        else:
            print("Input not valid! Please pick 1, 2 or 3!")
    except ValueError as e:
        print("Error: ", e)
    finally:
        random = input("Press return key to finish!")

if __name__ == "__main__":
    main()