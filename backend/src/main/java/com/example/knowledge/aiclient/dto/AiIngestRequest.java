package com.example.knowledge.aiclient.dto;

import java.util.Map;

public record AiIngestRequest(
        String document_id,
        String source,
        String content,
        String scope,
        Map<String, Object> metadata
) {}
