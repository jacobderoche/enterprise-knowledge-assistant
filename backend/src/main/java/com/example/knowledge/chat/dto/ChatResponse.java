package com.example.knowledge.chat.dto;

import com.example.knowledge.aiclient.dto.AiQueryResponse;
import java.util.List;

public record ChatResponse(
        String conversationId,
        String messageId,
        String answer,
        List<AiQueryResponse.Citation> citations,
        String model,
        boolean usedContext
) {}
