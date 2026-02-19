from flask import Flask, request, jsonify
import anthropic
from openai import OpenAI
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Math Tutor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            display: flex;
            height: 100vh;
        }
        
        .sidebar {
            width: 350px;
            background: white;
            padding: 2rem;
            overflow-y: auto;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
        }
        
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
            padding: 2rem;
        }
        
        h1 {
            color: #333;
            margin-bottom: 1.5rem;
            font-size: 1.8rem;
        }
        
        h2 {
            color: #555;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            margin-top: 1.5rem;
        }
        
        .api-section {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            color: #333;
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        input[type="password"],
        textarea,
        select {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }
        
        input[type="password"]:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        button {
            width: 100%;
            padding: 0.75rem 1rem;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.95rem;
            transition: background 0.3s;
            margin-bottom: 0.5rem;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        button.secondary {
            background: #f0f0f0;
            color: #333;
            margin: 0.25rem;
        }
        
        button.secondary:hover {
            background: #e0e0e0;
        }
        
        button.secondary.active {
            background: #667eea;
            color: white;
        }
        
        .mode-buttons {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        
        .mode-buttons button {
            flex: 1;
            margin: 0;
        }
        
        .problem-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }
        
        .problem-box h3 {
            font-size: 1rem;
            margin-bottom: 1rem;
            opacity: 0.9;
        }
        
        .problem-box p {
            font-size: 1.2rem;
            line-height: 1.6;
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .message {
            padding: 1rem;
            border-radius: 10px;
            word-wrap: break-word;
            max-width: 80%;
        }
        
        .student-message {
            background: #667eea;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 2px;
        }
        
        .tutor-message {
            background: #f0f0f0;
            color: #333;
            align-self: flex-start;
            border-bottom-left-radius: 2px;
        }
        
        .input-area {
            display: flex;
            gap: 0.5rem;
        }
        
        .input-area input {
            flex: 1;
            padding: 0.75rem;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            margin-bottom: 0;
        }
        
        .input-area button {
            flex: 0 0 80px;
            margin: 0;
        }
        
        .problems-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .problem-item {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }
        
        .problem-item button:first-child {
            flex: 1;
            margin: 0;
        }
        
        .problem-item button:last-child {
            flex: 0 0 50px;
            margin: 0;
        }
        
        .info {
            color: #666;
            padding: 1rem;
            background: #f9f9f9;
            border-radius: 6px;
            font-size: 0.9rem;
        }
        
        hr {
            border: none;
            height: 1px;
            background: #ddd;
            margin: 1.5rem 0;
        }
        
        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <div class="sidebar">
            <h1>📚 Math Tutor</h1>
            
            <div class="api-section">
                <h2>API Configuration</h2>
                
                <label>Choose AI:</label>
                <select id="aiChoice" onchange="updateAPIInput()">
                    <option value="claude">Claude (Anthropic)</option>
                    <option value="chatgpt">ChatGPT (OpenAI)</option>
                </select>
                
                <label id="apiLabel">Anthropic API Key:</label>
                <input type="password" id="apiKey" placeholder="Enter API key">
                <small id="apiLink"><a href="https://console.anthropic.com" target="_blank">Get Anthropic Key</a></small>
            </div>
            
            <div class="mode-buttons">
                <button class="secondary active" onclick="setMode('teacher')">👨‍🏫 Teacher</button>
                <button class="secondary" onclick="setMode('student')">👨‍🎓 Student</button>
            </div>
            
            <hr>
            
            <div id="teacherPanel">
                <h2>Add Problems</h2>
                <textarea id="problemInput" placeholder="Paste a word problem..."></textarea>
                <button onclick="addProblem()">➕ Add Problem</button>
                
                <h2>Problems</h2>
                <div class="problems-list" id="problemsList"></div>
            </div>
        </div>
        
        <!-- Main Area -->
        <div class="main">
            <div id="studentPanel">
                <div id="problemDisplay"></div>
                <h3>Let's solve this together!</h3>
                <div class="messages" id="messages"></div>
                <div class="input-area">
                    <input type="text" id="studentInput" placeholder="Type your response..." onkeypress="if(event.key==='Enter') sendMessage()">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <div id="teacherView" class="hidden">
                <h1>Teacher Control Panel</h1>
                <div class="info" id="teacherInfo">Add word problems using the sidebar to get started!</div>
            </div>
        </div>
    </div>
    
    <script>
        let mode = 'teacher';
        let problems = [];
        let currentProblemIndex = null;
        let messages = [];
        
        function setMode(newMode) {
            mode = newMode;
            document.querySelectorAll('.mode-buttons button').forEach((btn, i) => {
                btn.classList.toggle('active', (i === 0 && newMode === 'teacher') || (i === 1 && newMode === 'student'));
            });
            document.getElementById('teacherPanel').classList.toggle('hidden', newMode !== 'teacher');
            document.getElementById('studentPanel').classList.toggle('hidden', newMode !== 'student');
            document.getElementById('teacherView').classList.toggle('hidden', newMode !== 'teacher');
        }
        
        function updateAPIInput() {
            const choice = document.getElementById('aiChoice').value;
            const label = document.getElementById('apiLabel');
            const link = document.getElementById('apiLink');
            
            if (choice === 'claude') {
                label.textContent = 'Anthropic API Key:';
                link.innerHTML = '<a href="https://console.anthropic.com" target="_blank">Get Anthropic Key</a>';
            } else {
                label.textContent = 'OpenAI API Key:';
                link.innerHTML = '<a href="https://platform.openai.com/api-keys" target="_blank">Get OpenAI Key</a>';
            }
        }
        
        function addProblem() {
            const input = document.getElementById('problemInput');
            if (!input.value.trim()) return;
            
            problems.push(input.value.trim());
            input.value = '';
            currentProblemIndex = problems.length - 1;
            messages = [];
            renderProblems();
            updateTeacherInfo();
        }
        
        function renderProblems() {
            const list = document.getElementById('problemsList');
            list.innerHTML = problems.map((p, i) => `
                <div class="problem-item">
                    <button class="secondary ${i === currentProblemIndex ? 'active' : ''}" onclick="selectProblem(${i})">
                        Problem ${i + 1}
                    </button>
                    <button class="secondary" onclick="deleteProblem(${i})">❌</button>
                </div>
            `).join('');
        }
        
        function selectProblem(index) {
            currentProblemIndex = index;
            messages = [];
            renderProblems();
            renderProblemDisplay();
            document.getElementById('messages').innerHTML = '';
        }
        
        function deleteProblem(index) {
            problems.splice(index, 1);
            if (currentProblemIndex === index) {
                currentProblemIndex = problems.length > 0 ? 0 : null;
                messages = [];
            }
            renderProblems();
            updateTeacherInfo();
        }
        
        function renderProblemDisplay() {
            const display = document.getElementById('problemDisplay');
            if (currentProblemIndex === null) {
                display.innerHTML = '<div class="info">No problem selected yet</div>';
            } else {
                const problem = problems[currentProblemIndex];
                display.innerHTML = `
                    <div class="problem-box">
                        <h3>Problem ${currentProblemIndex + 1}</h3>
                        <p>${problem}</p>
                    </div>
                `;
            }
        }
        
        function updateTeacherInfo() {
            const info = document.getElementById('teacherInfo');
            if (problems.length === 0) {
                info.textContent = 'Add word problems using the sidebar to get started!';
            } else {
                info.textContent = `You have ${problems.length} problem(s) ready for students`;
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('studentInput');
            const text = input.value.trim();
            if (!text || currentProblemIndex === null) return;
            
            messages.push({role: 'student', content: text});
            input.value = '';
            renderMessages();
            
            const apiKey = document.getElementById('apiKey').value;
            if (!apiKey) {
                alert('Please set API key in sidebar');
                return;
            }
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        api_key: apiKey,
                        ai_choice: document.getElementById('aiChoice').value,
                        problem: problems[currentProblemIndex],
                        messages: messages
                    })
                });
                
                const data = await response.json();
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    messages.push({role: 'tutor', content: data.response});
                    renderMessages();
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
        
        function renderMessages() {
            const container = document.getElementById('messages');
            container.innerHTML = messages.map(msg => `
                <div class="message ${msg.role === 'student' ? 'student-message' : 'tutor-message'}">
                    ${msg.content}
                </div>
            `).join('');
            container.scrollTop = container.scrollHeight;
        }
        
        // Initialize
        renderProblemDisplay();
        updateTeacherInfo();
    </script>
</body>
</html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    api_key = data.get('api_key')
    ai_choice = data.get('ai_choice')
    problem = data.get('problem')
    messages = data.get('messages', [])
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 400
    
    system_prompt = f"You are an adaptive math tutor helping students solve word problems. Assess their language proficiency and math understanding. Scaffold their learning by praising effort, asking questions instead of giving answers, using simple language for ESOL students. Guide them through: 1. Understanding - What is the problem asking? 2. Identifying - What information do we have? 3. Planning - What operation will we use? 4. Solving - Work through the math. 5. Checking - Does our answer make sense? Keep responses short (2-3 sentences). Ask ONE question at a time. Current problem: {problem}"
    
    api_messages = []
    for msg in messages:
        api_messages.append({
            'role': 'user' if msg['role'] == 'student' else 'assistant',
            'content': msg['content']
        })
    
    try:
        if ai_choice == 'claude':
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-opus-4-20250805",
                max_tokens=500,
                system=system_prompt,
                messages=api_messages
            )
            tutor_message = response.content[0].text
        else:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                max_tokens=500,
                system=system_prompt,
                messages=api_messages
            )
            tutor_message = response.choices[0].message.content
        
        return jsonify({'response': tutor_message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
