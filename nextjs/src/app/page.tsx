"use client"
import React, { useState, useTransition } from 'react';
import { fetchVideoInfo, getStreamUrl, getDownloadUrl } from './actions';

interface VideoInfo {
  title: string;
  duration: number;
  formats_available: number;
  thumbnail?: string;
}

const DoomVideoStreamer = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [streamUrl, setStreamUrl] = useState('');
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [error, setError] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleGetInfo = async () => {
    if (!videoUrl) {
      setError('Please enter a video URL first');
      return;
    }

    setError('');
    startTransition(async () => {
      try {
        const info = await fetchVideoInfo(videoUrl);
        setVideoInfo(info);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to get video information');
      }
    });
  };

  const handleStream = async () => {
    if (!videoUrl) {
      setError('Please enter a video URL first');
      return;
    }

    setError('');
    try {
      const url = await getStreamUrl(videoUrl);
      setStreamUrl(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start video stream');
    }
  };

  const handleDownload = async () => {
    if (!videoUrl) {
      setError('Please enter a video URL first');
      return;
    }

    setError('');
    startTransition(async () => {
      try {
        const downloadUrl = await getDownloadUrl(videoUrl, videoInfo?.title);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.rel = 'noopener';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to download video');
      }
    });
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted to-background p-4 relative scanlines crt-flicker">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="doom-text text-4xl mb-2 doom-glow text-primary">
            VIDEO STREAMER
          </h1>
          <p className="doom-text text-muted-foreground">
            WATCH AND DOWNLOAD VIDEOS • SECURE & FAST
          </p>
        </div>

        {/* Main Interface */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1">
            <div className="doom-panel p-6 relative">
              <h2 className="doom-text text-xl mb-4 text-primary">ACTIONS</h2>

              {/* URL Input */}
              <div className="mb-6">
                <label className="doom-text text-sm block mb-2 text-muted-foreground">
                  Video URL:
                </label>
                <input
                  type="text"
                  placeholder="Paste your video URL here..."
                  value={videoUrl}
                  onChange={(e) => setVideoUrl(e.target.value)}
                  className="doom-input w-full p-3 text-sm focus:outline-none"
                />
              </div>

              {/* Action Buttons */}
              <div className="space-y-3">
                <button
                  onClick={handleGetInfo}
                  disabled={isPending}
                  className="doom-button w-full p-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isPending ? 'Loading...' : 'Get Video Info'}
                </button>

                <button
                  onClick={handleStream}
                  disabled={isPending}
                  className="doom-button w-full p-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Watch Video
                </button>

                <button
                  onClick={handleDownload}
                  disabled={isPending}
                  className="doom-button w-full p-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isPending ? 'Downloading...' : 'Download Video'}
                </button>
              </div>

              {/* Error Display */}
              {error && (
                <div className="mt-4 p-3 bg-destructive/20 border border-destructive text-destructive doom-text text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Video Info & Player */}
          <div className="lg:col-span-2 space-y-6">
            {/* Video Info Panel */}
            {videoInfo && (
              <div className="doom-panel p-6">
                <h2 className="doom-text text-xl mb-4 text-primary">Video Details</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="doom-text text-sm text-muted-foreground mb-1">Title:</h3>
                    <p className="text-sm font-mono break-words">{videoInfo.title}</p>
                  </div>
                  <div>
                    <h3 className="doom-text text-sm text-muted-foreground mb-1">Duration:</h3>
                    <p className="text-sm font-mono">{formatDuration(videoInfo.duration)}</p>
                  </div>
                  <div>
                    <h3 className="doom-text text-sm text-muted-foreground mb-1">Available Formats:</h3>
                    <p className="text-sm font-mono">{videoInfo.formats_available}</p>
                  </div>
                  {videoInfo.thumbnail && (
                    <div>
                      <h3 className="doom-text text-sm text-muted-foreground mb-1">Thumbnail:</h3>
                      <div className="relative w-full max-w-sm mx-auto">
                        <img
                          src={videoInfo.thumbnail}
                          alt="Video thumbnail"
                          className="w-6/10 h-auto max-h-32 object-cover border-2 border-border rounded"
                          onError={(e: React.SyntheticEvent<HTMLImageElement, Event>) => {
                            // Hide the image if it fails to load
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Video Player */}
            {streamUrl && (
              <div className="doom-panel p-6">
                <h2 className="doom-text text-xl mb-4 text-primary">Now Playing</h2>
                <div className="relative">
                  <video
                    controls
                    className="w-full border-2 border-border bg-black"
                    src={streamUrl}
                  >
                    Your browser does not support video playback.
                  </video>
                </div>
              </div>
            )}

            {/* Instructions */}
            <div className="doom-panel p-6">
              <h2 className="doom-text text-xl mb-4 text-primary">How to Use</h2>
              <div className="space-y-3 text-sm">
                <div className="flex items-start space-x-3">
                  <span className="doom-text text-primary text-xs mt-0.5">1.</span>
                  <div>
                    <span className="doom-text text-primary">Get Video Info:</span>
                    <span className="text-muted-foreground ml-2">Preview video details before downloading</span>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="doom-text text-primary text-xs mt-0.5">2.</span>
                  <div>
                    <span className="doom-text text-primary">Watch Video:</span>
                    <span className="text-muted-foreground ml-2">Stream video directly in your browser</span>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="doom-text text-primary text-xs mt-0.5">3.</span>
                  <div>
                    <span className="doom-text text-primary">Download Video:</span>
                    <span className="text-muted-foreground ml-2">Save video file to your device</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-xs text-muted-foreground doom-text">
          Enjoy watching and downloading your favorite videos
        </div>
      </div>
    </div>
  );
};

export default DoomVideoStreamer;
