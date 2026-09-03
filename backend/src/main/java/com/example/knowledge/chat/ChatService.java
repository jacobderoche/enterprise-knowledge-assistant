package com.example.knowledge.chat;

import com.example.knowledge.aiclient.AiServiceClient;
import com.example.knowledge.aiclient.dto.AiQueryRequest;
import com.example.knowledge.aiclient.dto.AiQueryResponse;
import com.example.knowledge.audit.AuditService;
import com.example.knowledge.chat.dto.ChatRequest;
import com.example.knowledge.chat.dto.ChatResponse;
import com.example.knowledge.security.AuthenticatedUser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

@Service
public class ChatService {

    private final ConversationRepository conversations;
    private final MessageRepository messages;
    private final AiServiceClient aiClient;
    private final AuditService audit;
    private final ObjectMapper objectMapper;

    public ChatService(ConversationRepository conversations, MessageRepository messages,
                       AiServiceClient aiClient, AuditService audit, ObjectMapper objectMapper) {
        this.conversations = conversations;
        this.messages = messages;
        this.aiClient = aiClient;
        this.audit = audit;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public ChatResponse chat(ChatRequest request, AuthenticatedUser user) {
        Conversation conversation = resolveConversation(request, user);

        messages.save(new Message(conversation.getId(), Message.Role.USER, request.message(), null));

        AiQueryResponse ai = aiClient.query(new AiQueryRequest(
                request.message(),
                new AiQueryRequest.Access(user.userId(), user.roles(), user.allowedScopes()),
                null,
                conversation.getId()));

        if (ai == null) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "AI service unavailable");
        }

        Message assistant = new Message(
                conversation.getId(), Message.Role.ASSISTANT, ai.answer(), serializeCitations(ai.citations()));
        messages.save(assistant);

        audit.record(user.userId(), "CHAT_QUERY", conversation.getId(),
                "usedContext=" + ai.used_context() + " citations=" + ai.citations().size());

        return new ChatResponse(
                conversation.getId(), assistant.getId(), ai.answer(), ai.citations(),
                ai.model(), ai.used_context());
    }

    @Transactional(readOnly = true)
    public List<Message> history(String conversationId, AuthenticatedUser user) {
        Conversation conversation = conversations.findById(conversationId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Conversation not found"));
        if (!conversation.getUserId().equals(user.userId()) && !user.roles().contains("admin")) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Not your conversation");
        }
        return messages.findByConversationIdOrderByCreatedAtAsc(conversationId);
    }

    private Conversation resolveConversation(ChatRequest request, AuthenticatedUser user) {
        if (request.conversationId() != null && !request.conversationId().isBlank()) {
            Conversation existing = conversations.findById(request.conversationId())
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Conversation not found"));
            if (!existing.getUserId().equals(user.userId())) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Not your conversation");
            }
            return existing;
        }
        String title = request.message().length() > 60
                ? request.message().substring(0, 60) : request.message();
        return conversations.save(new Conversation(user.userId(), title));
    }

    private String serializeCitations(List<AiQueryResponse.Citation> citations) {
        try {
            return objectMapper.writeValueAsString(citations);
        } catch (JsonProcessingException e) {
            return "[]";
        }
    }
}
