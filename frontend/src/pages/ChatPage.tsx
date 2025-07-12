import React, { useState, useEffect, useRef, type FormEvent } from "react";
import { getAnneResponse } from "../services/chatbot";
import "./ChatPage.css";

interface Message {
  id: number;
  text: string;
  sender: "user" | "anne";
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      text: "Hello, I'm here to listen. What would you like to talk about?",
      sender: "anne",
    },
  ]);
  const [inputValue, setInputValue] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll to the bottom whenever messages change
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);


  const [userQuestions, setUserQuestions] = useState<Message[]>([]);


  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    const trimmedInput = inputValue.trim();
    if (trimmedInput === "") return;


    const newUserMessage: Message = {
      id: Math.random() * 100,
      text: trimmedInput,
      sender: "user",
    };
    // console.log(newUserMessage)
    setMessages((prev) => [...prev, newUserMessage]);


    const previousQuestionsString = userQuestions
      .map((msg, index) => `${index + 1}. ${msg.text}`)
      .join("\n");

    setInputValue("");
    setIsTyping(true);


    const anneResponseText = await getAnneResponse(
      previousQuestionsString,
      trimmedInput
    );


    setUserQuestions((prev) => [...prev, newUserMessage]);

    const newAnneMessage: Message = {
      id: newUserMessage.id + 1,
      text: anneResponseText,
      sender: "anne",
    };
    // console.log(newAnneMessage)
    setMessages((prev) => [...prev, newAnneMessage]);
    setIsTyping(false);
  };


  return (
    <div className="chat-page-container">
      <div className="chat-window">
        <div className="chat-messages" ref={chatContainerRef}>
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-bubble-container ${message.sender}`}
            >
              <div className={`message-bubble ${message.sender}`}>
                {message.text}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message-bubble-container anne">
              <div className="message-bubble anne typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>
        <form className="chat-input-form" onSubmit={handleSendMessage}>
          <input
            type="text"
            className="chat-input"
            placeholder="Type your message here..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isTyping}
          />
          <button
            type="submit"
            className="send-button"
            disabled={isTyping || !inputValue.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPage;
