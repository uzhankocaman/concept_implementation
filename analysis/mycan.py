# import cantools
# import can
# import os
# from pprint import pprint 
# import sqlite3
# import pandas as pd

#     print(5)
# if key not in aggregated_data:
#     aggregated_data[key] = entry['decoded_data']
# else:
#     for param, value in entry['decoded_data'].items():
#         if param not in aggregated_data[key]:
#             aggregated_data[key][param] = value
#         else:
#             i = i + 1
#             aggregated_data[key][param] = value  

# final_data = []
# for (file, timestamp), decoded_data in aggregated_data.items():
#     final_data.append({
#         'file': file,
#         'timestamp': timestamp,
#         'decoded_data': decoded_data
#     })

# transformed_data = []

# for entry in final_data:
#     new_entry = {key: value for key, value in entry.items() if key != 'decoded_data'}
#     new_entry.update(entry['decoded_data'])
#     transformed_data.append(new_entry)



# def process_log_file(log_file_path):
#     with open(log_file_path, 'r') as file:
#         for line in file:
#             try:
#                 parts = line.strip().split(' ')
#                 timestamp = parts[0]
#                 can_interface = parts[1]
#                 frame_id, data = parts[2].split('#')
#                 frame_id = int(frame_id, 16) 
#                 data = bytes.fromhex(data.split(' ')[0]) 

#                 try:
#                     decoded_data = db.decode_message(frame_id, data)
#                     data_entry = {
#                         "file": os.path.basename(log_file_path),
#                         "timestamp": timestamp,
#                         "interface": can_interface,
#                         "frame_id": frame_id,
#                         "decoded_data": decoded_data
#                     }
#                     all_decoded_data.append(data_entry)
#                     print(decoded_data)
#                 except Exception as e:
#                     print(f"Error decoding frame: {e}")
#             except IndexError:
#                 print(log_file_path)




