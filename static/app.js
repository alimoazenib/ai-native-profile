// DOM Element References
const form = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('chat-messages');

const traceIntent = document.getElementById('trace-intent');
const traceCapability = document.getElementById('trace-capability');
const traceExternal = document.getElementById('trace-external');
const traceFields = document.getElementById('trace-fields');
const missingBox = document.getElementById('missing-box');
const traceMissing = document.getElementById('trace-missing');
const creativityBox = document.getElementById('creativity-box');
const matchScore = document.getElementById('match-score');
const matchedSkills = document.getElementById('matched-skills');

function setPrompt(text) {
    userInput.value = text;
    form.dispatchEvent(new Event('submit'));
}

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;

    appendMessage(query, 'user');
    userInput.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query })
        });
        const data = await response.json();

        appendMessage(data.answer, 'assistant');
        updateExplainability(data.trace);
    } catch (error) {
        appendMessage('خطایی در ارتباط با سرور رخ داد. لطفاً مجدداً تلاش کنید.', 'assistant');
    }
});

// Function to convert basic Markdown syntax to safe HTML elements
function formatMarkdown(text) {
    if (!text) return '';

    // 1. Sanitize text against XSS injection vulnerabilities
    let escaped = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // 2. Convert **bold** syntax to <strong> tags
    escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 3. Convert *italic* or _italic_ syntax to <em> tags
    escaped = escaped.replace(/(^|[^*])\*(?!\*)(.*?)\*/g, '$1<em>$2</em>');

    // 4. Transform Markdown list items into semantic unordered lists
    escaped = escaped.replace(/^[\*\-]\s+(.*)$/gm, '<li class="chat-li">$1</li>');
    escaped = escaped.replace(/((?:<li class="chat-li">.*<\/li>\s*)+)/g, '<ul class="chat-ul">$1</ul>');

    // 5. Replace newlines with break tags while cleaning up trailing line breaks after lists
    escaped = escaped.replace(/\n/g, '<br>');
    escaped = escaped.replace(/<\/ul><br>/g, '</ul>');

    return escaped;
}

function appendMessage(text, role) {
    const messageNode = document.createElement('div');
    messageNode.className = `message ${role}`;
    
    if (role === 'assistant') {
        // Render formatted HTML for agent responses
        messageNode.innerHTML = formatMarkdown(text);
    } else {
        // Enforce plain text for visitor input to prevent injection
        messageNode.innerText = text;
    }

    messagesContainer.appendChild(messageNode);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function updateExplainability(trace) {
    traceIntent.innerText = trace.intent || 'N/A';
    traceCapability.innerText = trace.capability || 'N/A';
    traceExternal.innerText = trace.external_service_used || 'None';

    // Populate retrieved fields list
    traceFields.innerHTML = '';
    if (trace.fields_read && trace.fields_read.length > 0) {
        trace.fields_read.forEach(field => {
            const li = document.createElement('li');
            li.innerText = `• ${field}`;
            traceFields.appendChild(li);
        });
    } else {
        traceFields.innerHTML = '<li>هیچ فیلدی خوانده نشد.</li>';
    }

    // Populate missing/refused facts
    if (trace.missing_facts && trace.missing_facts.length > 0) {
        missingBox.style.display = 'block';
        traceMissing.innerHTML = '';
        trace.missing_facts.forEach(missing => {
            const li = document.createElement('li');
            li.innerText = `• ${missing}`;
            traceMissing.appendChild(li);
        });
    } else {
        missingBox.style.display = 'none';
    }

    // Render creativity job fit breakdown
    if (trace.creativity_meta && trace.creativity_meta.match_score) {
        creativityBox.style.display = 'block';
        matchScore.innerText = `${trace.creativity_meta.match_score}%`;
        matchedSkills.innerHTML = (trace.creativity_meta.matched_skills || [])
            .map(skill => `<span class="badge">${skill}</span>`).join(' ');
    } else {
        creativityBox.style.display = 'none';
    }
}