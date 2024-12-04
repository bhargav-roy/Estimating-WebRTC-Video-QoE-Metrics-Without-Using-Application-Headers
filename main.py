import csv
import numpy as np

# Constants
LOOK_AHEAD = 15 # Max packets to look ahead for same-length packets (up to 15)
WINDOW_DURATION = 5   # Duration of the window in seconds (15 - 10)
LENGTH_DIFF = 15   # Allow up to 15 bytes difference in length

# File path to the exported CSV (replace with your actual file path)
filename = "Google_Meet_data.csv"  # Update with the path to your CSV file

# Load filtered packet data (based on your Wireshark export filter)
packets = []
Time = []
with open(filename, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        length = int(row["Length"])  # Replace "frame.len" with the actual column name for packet length
        source_ip = row["Source"]       # Replace with actual column name for source IP
        destination_ip = row["Destination"]  # Replace with actual column name for destination IP
        protocol = row["Protocol"]      # Replace with actual column name for protocol (TCP/SSLv2)
        time= row["Time"]               # Replace with actual column name for time
        # Filter based on the exported criteria
        if source_ip == "74.125.250.130" and destination_ip == "10.200.16.119" :  # 6 for TCP
            packets.append(length)
            Time.append(time)

# Debugging: Total packet count
print(f"Total Packets: {len(packets)}")

# Calculate frames
frame_count = 0
visited = [False] * len(packets)  # Track packets already grouped into frames
end_time=[]

# Calculate total packet size
total_packet_size = sum(packets)

# Iterate through packets to group them into frames
for i in range(len(packets)):
    if visited[i]:
        continue  # Skip already processed packets
    frame_length = packets[i]
    frame_count += 1  # Start a new frame
    visited[i] = True  # Mark the first packet as visited (this packet is counted as part of a frame)
    frame_packets = [i]  # Track packets in this frame

    temp_time=0
    
    # Look ahead to find matching packets within the allowable length difference
    for j in range(i + 1, min(i + LOOK_AHEAD + 1, len(packets))):
        if abs(packets[j] - frame_length) <= LENGTH_DIFF:  # Allow up to 15 bytes difference in length
            if not visited[j]:  # Only consider unvisited packets
                visited[j] = True
                frame_packets.append(j)
                temp_time = Time[j]

    if temp_time!=0:
        end_time.append(temp_time)
    
    # Debugging: Output frame details
    print(f"Frame {frame_count}: Length {frame_length}, Packets {len(frame_packets)}")


# Calculate bitrate
total_bits = total_packet_size * 8  # Convert bytes to bits
bit_rate = (total_bits / WINDOW_DURATION) / 1e6  # Convert bits to Mbps
print(f"Bit Rate: {bit_rate:.2f} Mbps")

# Calculate frame rate
frame_rate = frame_count / WINDOW_DURATION
print(f"Frame Rate: {frame_rate:.2f} frames per second")

print("End Time of consecutive Packets: ",end_time)
#frame jitter calculation
end_time_diff = []
for i in range(1,len(end_time)-1):
    end_time_diff.append(float(end_time[i+1])-float(end_time[i]))
jitter = np.std(np.array(end_time_diff))
print(f"Frame Jitter: {jitter:.2f} seconds")