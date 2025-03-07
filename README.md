# Podcast Summarizer

Welcome to my **Podcast Summarizer** repository! I'm an avid podcast listener, and I love tuning in while I jog or relax at home. My absolute favorite podcast is *The Diary of A CEO* — check it out [here](https://www.youtube.com/@TheDiaryOfACEO).

![podcast_summarizer.gif](podcast_summarizer.gif)

Ever listened to a podcast, got inspired by the insights shared, but then realized you can't remember anything afterward? I’ve found myself constantly replaying parts of the episode to take notes. That’s where this personal project comes in! It's designed to help you recall the key points from any podcast without having to replay the entire episode.

This program utilizes the following technologies:

* **Google's Gemini AI**: Chosen for its **large context window**, ideal for summarizing long-form content like hour-long podcasts.
    * [Gemini AI](https://deepmind.google/technologies/gemini/)
* **Prompt Engineering**: To structure the summary in an optimal, easily digestible format.
* **Whisper OpenAI**: A speech recognition model by OpenAI, used locally to convert audio to transcript.
    * [Whisper OpenAI](https://github.com/openai/whisper)
    * Note: While Whisper offers variations from tiny to turbo, this project currently uses "tiny" due to resource constraints. Testing other models requires a GPU, which is not available in my current environment (CPU with 8GB RAM).
* **youtube-transcript-api**: To obtain transcripts directly from YouTube.
* **yt-dlp**: To download audio from YouTube.
* **ffmpeg**: Required for Whisper OpenAI to convert audio to text.

---

## Environment

This project is developed and tested within **WSL (Windows Subsystem for Linux)**. Ensure your WSL environment is properly configured before running the script.

---

## Installation

1.  **Install Dependencies:**

    ```bash
    pip install youtube-transcript-api yt-dlp openai-whisper google-genai
    sudo apt install ffmpeg
    ```

2.  **API Key Setup:**

    * Obtain your Gemini AI API key from [here](https://ai.google.dev/gemini-api/docs/api-key).
    * Set the API key as an environment variable:

        ```bash
        export GEMINI_API_KEY="your_actual_api_key"
        ```

---

## Running the Script

Execute the summarizer with the following command:

```bash
python3 podcast_summarizer.py [youtube_link]
```

### Example:
```bash
python3 podcast_summarizer.py https://www.youtube.com/watch?v=ffgpqk5hZBE
```

**Note:** Ensure you use the **full video URL** (the one from the browser address bar), **not** the shortened sharing link.

---

## How It Works

1. **Transcript Retrieval**: The script first tries to fetch the transcript directly from YouTube using `YouTubeTranscriptApi`.
2. **Audio Download**: If no transcript is available, it downloads the audio using `yt-dlp`.
3. **Audio Conversion**: The `.mp3` audio file is converted to **16kHz mono** for optimal transcription using **FFmpeg**.
4. **Transcription**: The processed audio is transcribed locally using **Whisper Tiny**.
5. **Summarization**: The transcript is then processed by **Gemini 2.0 Flash**, which extracts key topics and insights.
6. **File Output**: The **summary** is saved as `summary.txt`.

---

## Performance Insights

- **Fast summarization** when a YouTube transcript is available.  
- **Slower processing** if the script has to **download, convert, and transcribe** audio manually.  
- On **low-spec machines (i5 CPU, 8GB RAM)**, **Whisper Tiny may crash** due to insufficient RAM when processing long audio files.  
- Using the **full YouTube video URL (instead of the sharing link)** helps avoid unnecessary audio processing.
