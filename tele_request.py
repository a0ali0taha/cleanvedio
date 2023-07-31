import requests

def send_file_to_telegram_channel(api_token, chat_id, file_path):
    url = f"https://api.telegram.org/bot{api_token}/sendDocument"
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': chat_id}

    response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
        print("File sent successfully!")
    else:
        print(f"Failed to send file. Error code: {response.status_code}")

# Replace these values with your API token and channel chat ID
api_token = "YOUR_API_TOKEN"
chat_id = "YOUR_CHANNEL_CHAT_ID"

# Replace "file_path" with the path to the file you want to send
file_path = "/path/to/your/file.txt"


send_file_to_telegram_channel(api_token, chat_id,'newv/الحرب العالمية الأولى باختصار.mp4')