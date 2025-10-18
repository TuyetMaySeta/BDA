-- Bảng videos
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    channel_name VARCHAR(255),
    full_transcript TEXT,
    duration INTEGER,
    published_at TIMESTAMP,
    summary TEXT,
    embedding VECTOR (1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bảng transcript_chunks
CREATE TABLE IF NOT EXISTS transcript_chunks (
    id SERIAL PRIMARY KEY,
    video_id INTEGER NOT NULL REFERENCES videos (id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    start_time FLOAT,
    end_time FLOAT,
    text TEXT NOT NULL,
    embedding VECTOR (1536),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_video_id ON transcript_chunks (video_id);

CREATE INDEX idx_chunk_index ON transcript_chunks (video_id, chunk_index);

CREATE INDEX idx_video_url ON videos (url);

CREATE INDEX ON videos USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX ON transcript_chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Trigger tự động update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chunks_updated_at BEFORE UPDATE ON transcript_chunks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();