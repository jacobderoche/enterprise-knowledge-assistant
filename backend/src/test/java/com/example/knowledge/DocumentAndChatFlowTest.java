package com.example.knowledge;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.knowledge.aiclient.AiServiceClient;
import com.example.knowledge.aiclient.dto.AiIngestResponse;
import com.example.knowledge.aiclient.dto.AiQueryRequest;
import com.example.knowledge.aiclient.dto.AiQueryResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class DocumentAndChatFlowTest {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    ObjectMapper objectMapper;

    @MockBean
    AiServiceClient aiClient;

    private static org.springframework.test.web.servlet.request.RequestPostProcessor employee() {
        return jwt()
                .jwt(j -> j.subject("u1").claim("roles", List.of("employee")))
                .authorities(new SimpleGrantedAuthority("ROLE_EMPLOYEE"));
    }

    @Test
    void unauthenticatedRequestIsRejected() throws Exception {
        mockMvc.perform(get("/api/documents"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void uploadDocumentForwardsToAiServiceAndPersists() throws Exception {
        when(aiClient.ingest(any())).thenReturn(new AiIngestResponse("doc", List.of(), 3));

        String payload = objectMapper.writeValueAsString(java.util.Map.of(
                "title", "Employee Handbook",
                "source", "handbook.md",
                "content", "Employees get 20 days PTO per year.",
                "scope", "public"));

        mockMvc.perform(post("/api/documents").with(employee())
                        .contentType(MediaType.APPLICATION_JSON).content(payload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.title").value("Employee Handbook"))
                .andExpect(jsonPath("$.chunkCount").value(3));

        mockMvc.perform(get("/api/documents").with(employee()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Employee Handbook"));
    }

    @Test
    void chatReturnsCitedAnswerAndStoresHistory() throws Exception {
        var citation = new AiQueryResponse.Citation("c1", "doc", "handbook.md", 0.92, "20 days PTO");
        when(aiClient.query(any(AiQueryRequest.class)))
                .thenReturn(new AiQueryResponse("Employees get 20 days PTO [1]", List.of(citation),
                        null, "offline-extractive", true));

        String payload = objectMapper.writeValueAsString(java.util.Map.of("message", "How much PTO?"));

        String response = mockMvc.perform(post("/api/chat").with(employee())
                        .contentType(MediaType.APPLICATION_JSON).content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.usedContext").value(true))
                .andExpect(jsonPath("$.citations[0].document_id").value("doc"))
                .andExpect(jsonPath("$.answer").value("Employees get 20 days PTO [1]"))
                .andReturn().getResponse().getContentAsString();

        String conversationId = objectMapper.readTree(response).get("conversationId").asText();

        mockMvc.perform(get("/api/chat/" + conversationId + "/messages").with(employee()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].role").value("USER"))
                .andExpect(jsonPath("$[1].role").value("ASSISTANT"));
    }
}
