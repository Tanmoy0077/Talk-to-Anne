const API_ENDPOINT = "http://localhost:8000/api/chat";

const defaultErrorResponse =
  "I'm sorry, I seem to be offline at the moment. Please try again later.";

export const getAnneResponse = async (userInput: string): Promise<string> => {
  try {
    const response = await fetch(API_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: userInput }),
    });

    if (!response.ok) {
      console.error("API Error:", response.status, response.statusText);
      return defaultErrorResponse;
    }

    const data = await response.json();

    // Ensure the response has the expected format
    if (data && typeof data.response === "string") {
      return data.response;
    } else {
      console.error("Invalid response format from API:", data);
      return "I'm not sure how to respond to that. Could you try rephrasing?";
    }
  } catch (error) {
    console.error("Error fetching response from chatbot API:", error);
    return defaultErrorResponse;
  }
};
