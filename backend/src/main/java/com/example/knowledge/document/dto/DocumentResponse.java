package com.example.knowledge.document.dto;

import com.example.knowledge.document.Document;
import java.time.Instant;

public record DocumentResponse(
        String id,
        String title,
        String source,
        String scope,
        int chunkCount,
        Instant createdAt
) {
    public static DocumentResponse from(Document d) {
        return new DocumentResponse(
                d.getId(), d.getTitle(), d.getSource(), d.getScope(), d.getChunkCount(), d.getCreatedAt());
    }
}
