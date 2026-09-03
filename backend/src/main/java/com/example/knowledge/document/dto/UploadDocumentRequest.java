package com.example.knowledge.document.dto;

import jakarta.validation.constraints.NotBlank;

public record UploadDocumentRequest(
        @NotBlank String title,
        @NotBlank String source,
        @NotBlank String content,
        String scope
) {
    public String scopeOrDefault() {
        return (scope == null || scope.isBlank()) ? "public" : scope;
    }
}
