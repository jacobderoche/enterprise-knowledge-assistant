package com.example.knowledge.feedback.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record FeedbackRequest(
        @NotBlank String messageId,
        @Min(-1) @Max(1) int rating,
        String comment
) {}
