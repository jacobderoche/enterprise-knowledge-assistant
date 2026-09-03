package com.example.knowledge.aiclient.dto;

import java.util.List;

public record AiIngestResponse(
        String document_id,
        List<Chunk> chunks,
        int chunk_count
) {
    public record Chunk(String chunk_id, int ordinal) {}
}
