package com.example.knowledge.aiclient;

import com.example.knowledge.aiclient.dto.AiIngestRequest;
import com.example.knowledge.aiclient.dto.AiIngestResponse;
import com.example.knowledge.aiclient.dto.AiQueryRequest;
import com.example.knowledge.aiclient.dto.AiQueryResponse;
import java.time.Duration;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

/** Blocking client wrapper over the Python AI service. */
@Component
public class AiServiceClient {

    private final WebClient webClient;

    public AiServiceClient(WebClient aiWebClient) {
        this.webClient = aiWebClient;
    }

    public AiIngestResponse ingest(AiIngestRequest request) {
        return webClient.post()
                .uri("/ingest")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AiIngestResponse.class)
                .block(Duration.ofSeconds(30));
    }

    public AiQueryResponse query(AiQueryRequest request) {
        return webClient.post()
                .uri("/query")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AiQueryResponse.class)
                .block(Duration.ofSeconds(60));
    }
}
