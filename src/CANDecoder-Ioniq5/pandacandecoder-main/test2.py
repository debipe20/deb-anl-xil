import pandas as pd

# Sample DataFrame
data = {
    'TimeStamps': ['2024-01-01 12:00:00', '2024-01-01 12:01:00', '2024-01-01 12:02:00',
                   '2024-01-01 12:03:00', '2024-01-01 12:04:00', '2024-01-01 12:05:00',
                   '2024-01-01 12:06:00', '2024-01-01 12:07:00', '2024-01-01 12:08:00',
                   '2024-01-01 12:09:00', '2024-01-01 12:10:00', '2024-01-01 12:11:00',
                   '2024-01-01 12:12:00', '2024-01-01 12:13:00'],
    'PandaNum': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7],
    'MessageID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    'Bus': [101, 101, 102, 102, 103, 103, 104, 104, 105, 105, 106, 106, 107, 107],
    'MessageLength': [3, 3, 7, 3, 8, 3, 5, 5, 5, 8, 4, 2, 7, 3],
    'Message': ['Car', 'jon', 'HelloSam', 'how', 'HelloSon', 'are', 'youJo', 'doing', 'today', 'Hellopink', 'this', 'is', 'youhell', 'red']
}

df = pd.DataFrame(data)

# Function to merge messages between "Hello" and "you"
def merge_messages(messages):
    result = ""
    start = False
    for message in messages:
        if "Hello" in message:
            result += message[message.find("Hello"):]
            start = True
        elif "you" in message and start:
            result += message[:message.find("you") + len("you")]
            start = False
        elif start:
            result += message
    return result.strip()  # Strip leading/trailing spaces

# Group by consecutive "Hello" and "you" occurrences
df['Group'] = (df['Message'].str.contains('Hello') | df['Message'].str.contains('you')).cumsum()

# Aggregate grouped messages
merged_df = df.groupby('Group').agg({
    'TimeStamps': 'first',
    'PandaNum': 'first',
    'MessageID': 'first',
    'Bus': 'first',
    'MessageLength': 'sum',
    'Message': merge_messages
}).reset_index(drop=True)

# Remove rows with empty message
merged_df = merged_df[merged_df['Message'] != ""]

print(merged_df)
