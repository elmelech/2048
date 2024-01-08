import subprocess

# List to store the output values
output_values = []

# Run GameManager.py 10 times and capture the console output
i = 1
while i < 5:
    result = subprocess.check_output(["python3", "GameManager.py"], text=True, shell=True).strip()
    output = int(result)  # Convert the output to an integer
    print("Test number " + str(i) + ": max tile is " + str(output))
    i += 1
    output_values.append(output)  # Append the output to the list

# Print the list of output values
print("Output values from each execution:")
print(output_values)
