from google import genai
from google.genai import types
from youtube_transcript_api import YouTubeTranscriptApi
import sys
import yt_dlp
import whisper
import subprocess
import os
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: Missing API key. Set GEMINI_API_KEY as an environment variable.")
    sys.exit(1)


# Check if the user provided a YouTube link
if len(sys.argv) < 2:
    print("Usage: python3 get_transcript.py [YouTube Link]")
    sys.exit(1)

# System instruction for Gemini
system_instruction = """You are given a youtube podcast transcript. Your task is to summarize the podcast.
This podcast usually contains multiple key topics.
The summarize the podcast following format:
Topic 1: Topic name
    Point 1: Point 1 of the topic
    Point 2: Point 2 of the topic
Topic 2:
    Point 1: Point 1 of the topic
    Point 2: Point 2 of the topic
    Point 3: Point 3 of the topic
Topic 3:
...
You should summarize the podcast in a concise manner.
If you are unable to summarize the podcast, please state that you are unable to do so."""

# Configuration for Gemini
genai_config = types.GenerateContentConfig(
    system_instruction=system_instruction,
    temperature=1,
    top_p=0.9,
    )

# Initialize the Gemini client
client = genai.Client(api_key=api_key)

# Get the YouTube URL from command-line arguments
youtube_url = sys.argv[1]
audio_file = "audio"
processed_audio = "audio.wav"

# Function to get the transcript of a YouTube podcast
def get_transcript(youtube_link):
    """This function will get the transcript of the podcast from the youtube link
    args:
        youtube_link: the youtube link of the podcast
    returns:
        transcript: the transcript of the podcast"""
    video_id = youtube_link.split('=')[-1]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([line['text'] for line in transcript])
    return transcript

# Function to download YouTube audio using yt-dlp if the transcript is not available
def download_audio(url, output_path):
    """This function will download the audio of the podcast from the youtube link
    args:
        url: the youtube link of the podcast
        output_path: the output path of the audio file"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '32',  # Lower quality for speed
        }],
        'outtmpl': output_path
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Function to convert audio to 16kHz mono (optimized for Whisper)
def preprocess_audio(input_path, output_path):
    """This function will preprocess the audio to 16kHz mono
    args:
        input_path: the input path of the audio file
        output_path: the output path of the processed audio file"""
    command = [
        "ffmpeg", "-i", input_path+".mp3",
        "-ar", "16000", "-ac", "1",  # Convert to 16kHz mono
        "-b:a", "32k",  # Lower bitrate for speed
        output_path, "-y"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Function to transcribe audio using Whisper Tiny
def transcribe_audio(file_path):
    """This function will transcribe the audio using Whisper Tiny model
    args:
        file_path: the path of the audio file
    returns:
        result["text"]: the transcribed text of the audio"""
    model = whisper.load_model("tiny")  # Fastest model
    result = model.transcribe(file_path, fp16=False)  # Disable FP16 for CPU
    return result["text"]

# Function to summarize the podcast using Gemini
def summarize(transcript):
    """This function will summarize the podcast
    args:
        transcript: the transcript of the podcast
    returns:
        summary: the summary of the podcast"""

    try:
        response = client.models.generate_content(
            model = "gemini-2.0-flash",
            config = genai_config,
            contents= transcript
            )
        return response.text
    except ValueError as e:
        return "Unable to summarize the podcast. Please try again later." 
      
# Download the transcript if available, otherwise download the audio and transcribe it
try:
    print("📝 Getting transcript...")
    transcript = get_transcript(youtube_url)
    print("✅ Transcript obtained successfully.")
except Exception as e:
    print("Unable to get the transcript of the podcast. Obtaining to audio to create transcription, so be patient.")
    # Download, preprocess, and transcribe the audio
    print("📥 Downloading audio...")
    download_audio(youtube_url, audio_file)

    print("🎵 Processing audio (downsampling)...")
    preprocess_audio(audio_file, processed_audio)

    print("📝 Transcribing with Whisper Tiny...")
    transcript = transcribe_audio(processed_audio)


# Summarize the podcast
print("\n🔍 Summarizing podcast...")
summary = summarize(transcript)

# Print and save the summary
print("\n📝 Summary:\n" + summary)

# Save summary to a file
with open("summary.txt", "w") as f:
    f.write(summary)

print("\n✅ Summary saved as summary.txt")

# Clean up the audio files
if os.path.exists(audio_file):
    os.remove(audio_file)
if os.path.exists(processed_audio):
    os.remove(processed_audio)