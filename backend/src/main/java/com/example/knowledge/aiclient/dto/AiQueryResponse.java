package com.example.knowledge.aiclient.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record AiQueryResponse(
        String answer,
        List<Citation> citations,
        String conversation_id,
        String model,
        boolean used_context
) {
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record Citation(
            String chunk_id,
            String document_id,
            String source,
            double score,
            String snippet
    ) {}
}
