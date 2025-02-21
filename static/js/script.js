document.addEventListener("DOMContentLoaded", function () {
    let inputBX = document.querySelector("#inputBX");
    let list = document.querySelector("#list");

    // Adiciona evento de Enter para criar uma nova tarefa
    inputBX.addEventListener("keyup", function (event) {
        if (event.key === "Enter" && this.value.trim() !== "") {
            addTask(this.value.trim());
            this.value = "";
        }
    });

    function addTask(taskText) {
        fetch("/add_task", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: taskText, completed: false })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    createTaskElement(data.taskId, taskText, false);
                } else {
                    console.error("Erro ao adicionar a tarefa no servidor");
                }
            })
            .catch(error => console.error("Erro na requisição:", error));
    }

    function createTaskElement(taskId, taskText, completed) {
        let listItem = document.createElement("li");
        listItem.setAttribute("data-id", taskId);
        listItem.classList.add("task-item");
        if (completed) {
            listItem.classList.add("done");
        }

        listItem.innerHTML = `
            <span class="task-text">${taskText}</span>
            <div class="buttons">
                <button class="complete-btn">✔</button>
                <button class="delete">❌</button>
            </div>
        `;

        list.appendChild(listItem);

        listItem.querySelector(".complete-btn").addEventListener("click", function () {
            completeTask(taskId, listItem);
        });

        listItem.querySelector(".delete").addEventListener("click", function () {
            deleteTask(taskId, listItem);
        });
    }

    function completeTask(taskId, listItem) {
        fetch(`/complete_task/${taskId}`, { method: "POST" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    listItem.classList.toggle("done", data.completed);
                } else {
                    console.error("Erro ao marcar a tarefa como concluída");
                }
            })
            .catch(error => console.error("Erro:", error));
    }

    function deleteTask(taskId, listItem) {
        fetch(`/delete_task/${taskId}`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    listItem.remove();
                } else {
                    console.error("Erro ao remover tarefa:", data.error);
                }
            })
            .catch(error => console.error("Erro ao remover tarefa:", error));
    }

    // Adiciona eventos para as tarefas carregadas do servidor
    document.querySelectorAll(".task-item").forEach(listItem => {
        let taskId = listItem.getAttribute("data-id");

        listItem.querySelector(".complete-btn").addEventListener("click", function () {
            completeTask(taskId, listItem);
        });

        listItem.querySelector(".delete").addEventListener("click", function () {
            deleteTask(taskId, listItem);
        });
    });
});
