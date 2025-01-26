import re
import csv

def parse_log_to_csv(log_file: str, csv_file: str):
    pattern = re.compile(
        r"Processing (\S+).*?Time: ([\d.]+)s.*?Best cost: ([\d.]+).*?Optimal: (\d+) → Deviation: ([\d.]+)%",
        re.DOTALL
    )
    
    data = []
    with open(log_file, 'r') as f:
        content = f.read()
        matches = re.findall(pattern, content)
        for match in matches:
            task_name = match[0]
            time = float(match[1])
            best_cost = float(match[2])
            optimal = int(match[3])
            deviation = float(match[4])
            data.append([task_name, time, best_cost, optimal, deviation])
    
    # Запись в CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Task", "Time (s)", "Best Cost", "Optimal Cost", "Deviation (%)"])
        writer.writerows(data)

# Пример вызова
parse_log_to_csv("./B.txt", "./B.csv")