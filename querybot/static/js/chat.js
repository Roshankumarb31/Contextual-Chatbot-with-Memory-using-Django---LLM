function handleKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function sendMessage() {
    const messageInput = document.getElementById("message");
    const messageText = messageInput.value.trim();
    if (!messageText) return;

    const chat = document.getElementById("chat");

    // Append user message
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "user");
    messageDiv.textContent = messageText;
    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
    messageInput.value = "";

    // Fake Typing Animation
    const botMessage = document.createElement("div");
    botMessage.classList.add("message", "bot");

    const typingAnimation = document.createElement("div");
    typingAnimation.classList.add("typing-animation");
    typingAnimation.innerHTML = `
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    `;
    botMessage.appendChild(typingAnimation);
    chat.appendChild(botMessage);
    chat.scrollTop = chat.scrollHeight;

    // Send message to Django backend
    fetch("/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: messageText })
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(() => {
            botMessage.innerHTML = parseMarkdown(data.response);
            chat.scrollTop = chat.scrollHeight;
            if (data.properties && Array.isArray(data.properties)) {
                displayProperties(data.properties);
            }
        }, 1000);
    });
}

function parseMarkdown(text) {
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold **text**
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Italic *text*
    text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>'); // Links [text](url)
    text = text.replace(/\n/g, '<br>'); // Line breaks
    return text;
}

function displayProperties(properties) {
    const chat = document.getElementById("chat");
    properties.forEach(property => {
        const propertyCard = document.createElement("div");
        propertyCard.classList.add("property-card");
        propertyCard.style.display = "flex";
        propertyCard.style.justifyContent = "space-between";
        propertyCard.style.alignItems = "center";
        propertyCard.style.gap = "15px";
        propertyCard.style.padding = "10px";
        propertyCard.style.border = "1px solid #ddd";
        propertyCard.style.borderRadius = "10px";
        propertyCard.style.marginBottom = "10px";
        propertyCard.style.position = "relative";
        
        propertyCard.innerHTML = `
            <img src="${property.image}" alt="Property Image" style="width: 60px; height: 60px; border-radius: 8px; object-fit: cover;">
            <div style="flex: 1;">
                <h3>${property.name}</h3>
                <p><strong>Location:</strong> ${property.locality}</p>
                <p><strong>Price:</strong> ${property.price_in_rs}</p>
                <p><strong>Size:</strong> ${property.price_size} sqft</p>
            </div>
            <button 
                onclick="window.open('${property.url}', '_blank')"
                style="position: absolute; bottom: 10px; right: 10px; padding: 6px 12px; background-color: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer;">
                View
            </button>
        `;
        chat.appendChild(propertyCard);
    });
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const chat = document.getElementById("chat");

        // Append user image message
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", "user");

        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.alt = "Uploaded Image";
        img.style.maxWidth = "200px";
        img.style.borderRadius = "8px";

        messageDiv.appendChild(img);
        chat.appendChild(messageDiv);
        chat.scrollTop = chat.scrollHeight;

        // Create FormData for image upload
        const formData = new FormData();
        formData.append("image", file);

        // Send image to Django backend
        // fetch("/upload-image/", {
        //     method: "POST",
        //     body: formData
        // })
        // .then(response => response.json())
        // .then(data => {
        //     const botMessage = document.createElement("div");
        //     botMessage.classList.add("message", "bot");
        //     if (data.response) {
        //         botMessage.innerHTML = parseMarkdown(data.response);
        //         if (data.properties && Array.isArray(data.properties)) {
        //             displayProperties(data.properties);
        //         }
        //     } else {
        //         botMessage.textContent = "Error uploading image.";
        //     }
        //     chat.appendChild(botMessage);
        //     chat.scrollTop = chat.scrollHeight;
        // })
        // .catch(error => {
        //     const botMessage = document.createElement("div");
        //     botMessage.classList.add("message", "bot");
        //     botMessage.textContent = "An error occurred while uploading the image.";
        //     chat.appendChild(botMessage);
        //     chat.scrollTop = chat.scrollHeight;
        // });
        fetch("/upload-image/", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            const botMessage = document.createElement("div");
            botMessage.classList.add("message", "bot");
            if (data.response) {
                botMessage.innerHTML = parseMarkdown(data.response);
                if (data.properties && Array.isArray(data.properties)) {
                    displayProperties(data.properties);
                }
            } else {
                botMessage.textContent = "Error uploading image.";
            }
            chat.appendChild(botMessage);
            chat.scrollTop = chat.scrollHeight;
        })
        .catch(error => {
            const botMessage = document.createElement("div");
            botMessage.classList.add("message", "bot");
            botMessage.textContent = "An error occurred while uploading the image.";
            chat.appendChild(botMessage);
            chat.scrollTop = chat.scrollHeight;
        });
    }
}

function appendMessage(content, sender = 'bot') {
    const chat = document.getElementById("chat");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);

    // 🪄 Render Markdown to HTML
    const rendered = marked.parse(content);
    messageDiv.innerHTML = rendered;

    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
}
