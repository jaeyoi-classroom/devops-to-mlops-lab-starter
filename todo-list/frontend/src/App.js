import React, { useState, useEffect } from "react";
import "./App.css";

// Flask API 주소
const API_URL = "/api/todos";  // Flask API 서버와 맞춤

function App() {
  const [todos, setTodos] = useState([]);  // TODO 목록 상태
  const [newTask, setNewTask] = useState("");  // 새로운 TODO 상태

  // API로부터 TODO 목록을 불러오는 함수
  const fetchTodos = async () => {
    const response = await fetch(API_URL);
    const data = await response.json();
    setTodos(data);
  };

  // 새로운 TODO 추가
  const addTodo = async (task) => {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ task }),
    });
    const data = await response.json();
    setTodos([...todos, data.todo]);
    setNewTask("");  // 입력 필드 초기화
  };

  // TODO 완료 상태 업데이트
  const toggleComplete = async (id, completed) => {
    await fetch(`${API_URL}/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ completed }),
    });
    fetchTodos();  // 목록 갱신
  };

  // TODO 삭제
  const deleteTodo = async (id) => {
    await fetch(`${API_URL}/${id}`, {
      method: "DELETE",
    });
    fetchTodos();  // 목록 갱신
  };

  // 컴포넌트가 마운트될 때 TODO 목록을 불러옴
  useEffect(() => {
    fetchTodos();
  }, []);

  return (
    <div className="App">
      <h1>TODO List</h1>
      <input
        type="text"
        value={newTask}
        onChange={(e) => setNewTask(e.target.value)}
        placeholder="Enter a new task"
      />
      <button onClick={() => addTodo(newTask)}>Add Task</button>

      <ul>
        {todos.map((todo) => (
          <li key={todo.id}>
            <span
              style={{
                textDecoration: todo.completed ? "line-through" : "none",
              }}
            >
              {todo.task}
            </span>
            <button onClick={() => toggleComplete(todo.id, !todo.completed)}>
              {todo.completed ? "Undo" : "Complete"}
            </button>
            <button onClick={() => deleteTodo(todo.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
