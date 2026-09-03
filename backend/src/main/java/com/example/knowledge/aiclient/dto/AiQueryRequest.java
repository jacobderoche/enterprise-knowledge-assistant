package com.example.knowledge.aiclient.dto;

import java.util.List;

public record AiQueryRequest(
        String query,
        Access access,
        Integer top_k,
        String conversation_id
) {
    public record Access(String user_id, List<String> roles, List<String> allowed_scopes) {}
}
