import csv

# Open the CSV file
with open('main.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    next(csv_reader)  # Skip the header row

    # Generate SQL INSERT statements
    for row in csv_reader:
        print(f"INSERT INTO table_name (column1, column2, ...) VALUES ('{row[0]}', '{row[1]}', ...);")
