package com.example.knowledge.chat;

import com.example.knowledge.chat.dto.ChatRequest;
import com.example.knowledge.chat.dto.ChatResponse;
import com.example.knowledge.security.AuthenticatedUser;
import jakarta.validation.Valid;
import java.util.List;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/chat")
public class ChatController {

    private final ChatService service;

    public ChatController(ChatService service) {
        this.service = service;
    }

    @PostMapping
    public ChatResponse chat(@Valid @RequestBody ChatRequest request, Authentication authentication) {
        return service.chat(request, AuthenticatedUser.from(authentication));
    }

    @GetMapping("/{conversationId}/messages")
    public List<Message> history(@PathVariable String conversationId, Authentication authentication) {
        return service.history(conversationId, AuthenticatedUser.from(authentication));
    }
}
