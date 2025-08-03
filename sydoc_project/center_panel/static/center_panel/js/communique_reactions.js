document.addEventListener('DOMContentLoaded', function() {
    // Get all reaction forms
    const reactionForms = document.querySelectorAll('.reaction-form');
    
    // Add event listener to each form
    reactionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(form);
            const reactionType = formData.get('reaction_type');
            
            // Send AJAX request
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update like/dislike counts
                    document.querySelector('#like-count-display span').textContent = data.like_count;
                    document.querySelector('#dislike-count-display span').textContent = data.dislike_count;
                    
                    // Get all buttons
                    const likeButton = document.querySelector('button[value="like"]').closest('form').querySelector('button');
                    const dislikeButton = document.querySelector('button[value="dislike"]').closest('form').querySelector('button');
                    const removeForm = document.querySelector('button[value="remove"]')?.closest('form');
                    
                    // Reset all buttons
                    likeButton.classList.remove('bg-green-100', 'text-green-800');
                    likeButton.classList.add('bg-gray-100', 'text-gray-600', 'hover:bg-green-50');
                    dislikeButton.classList.remove('bg-red-100', 'text-red-800');
                    dislikeButton.classList.add('bg-gray-100', 'text-gray-600', 'hover:bg-red-50');
                    
                    // Update button styles based on reaction
                    if (reactionType === 'like') {
                        likeButton.classList.remove('bg-gray-100', 'text-gray-600', 'hover:bg-green-50');
                        likeButton.classList.add('bg-green-100', 'text-green-800');
                        
                        // Show remove button if it exists or create it
                        if (!removeForm) {
                            const newRemoveForm = createRemoveForm(form.action);
                            form.parentNode.appendChild(newRemoveForm);
                        } else {
                            removeForm.style.display = 'block';
                        }
                    } else if (reactionType === 'dislike') {
                        dislikeButton.classList.remove('bg-gray-100', 'text-gray-600', 'hover:bg-red-50');
                        dislikeButton.classList.add('bg-red-100', 'text-red-800');
                        
                        // Show remove button if it exists or create it
                        if (!removeForm) {
                            const newRemoveForm = createRemoveForm(form.action);
                            form.parentNode.appendChild(newRemoveForm);
                        } else {
                            removeForm.style.display = 'block';
                        }
                    } else if (reactionType === 'remove') {
                        // Hide remove button
                        removeForm.style.display = 'none';
                    }
                    
                    // Show success message
                    const messageContainer = document.createElement('div');
                    messageContainer.className = 'mt-2 text-sm text-green-600';
                    messageContainer.textContent = 'Réaction enregistrée avec succès.';
                    
                    // Remove existing messages
                    const existingMessages = document.querySelectorAll('.text-green-600, .text-red-600, .text-amber-600');
                    existingMessages.forEach(msg => msg.remove());
                    
                    // Add new message
                    const reactionsContainer = document.querySelector('.flex.items-center.justify-between');
                    reactionsContainer.appendChild(messageContainer);
                    
                    // Remove message after 3 seconds
                    setTimeout(() => {
                        messageContainer.remove();
                    }, 3000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Show error message
                const messageContainer = document.createElement('div');
                messageContainer.className = 'mt-2 text-sm text-red-600';
                messageContainer.textContent = 'Une erreur est survenue. Veuillez réessayer.';
                
                // Remove existing messages
                const existingMessages = document.querySelectorAll('.text-green-600, .text-red-600, .text-amber-600');
                existingMessages.forEach(msg => msg.remove());
                
                // Add new message
                const reactionsContainer = document.querySelector('.flex.items-center.justify-between');
                reactionsContainer.appendChild(messageContainer);
            });
        });
    });
    
    // Function to create a remove reaction form
    function createRemoveForm(action) {
        const form = document.createElement('form');
        form.method = 'post';
        form.action = action;
        form.className = 'reaction-form';
        
        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrfmiddlewaretoken';
        csrf.value = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'reaction_type';
        input.value = 'remove';
        
        const button = document.createElement('button');
        button.type = 'submit';
        button.className = 'px-3 py-1 rounded-md flex items-center bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors duration-200';
        
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'w-4 h-4 mr-1');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('viewBox', '0 0 24 24');
        
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('stroke-linecap', 'round');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('d', 'M6 18L18 6M6 6l12 12');
        
        svg.appendChild(path);
        button.appendChild(svg);
        button.appendChild(document.createTextNode('Retirer'));
        
        form.appendChild(csrf);
        form.appendChild(input);
        form.appendChild(button);
        
        return form;
    }
});
