document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('discussion-form');
  
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
  
      const category = document.getElementById('category').value;
      const title = document.getElementById('title').value;
      const body = document.getElementById('body').value;
  
      try {
        const response = await fetch('/api/posts/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({ category, title, body }),
        });
  
        const data = await response.json();
  
        if (response.ok) {
          alert('Discussion created successfully!');
          form.reset();
  
          document.getElementById('body').style.height = 'auto';
  
          const modalEl = document.getElementById('modaltest');
          const modalInstance = bootstrap.Modal.getInstance(modalEl);
          if (modalInstance) modalInstance.hide();
        } else {
          alert('Error: ' + data.error);
        }
      } catch (err) {
        alert('Network error: ' + err.message);
      }
    });
  
    function getCookie(name) {
      const cookieStr = document.cookie;
      const cookies = cookieStr.split(';');
      for (let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if (key === name) return decodeURIComponent(value);
      }
      return null;
    }
  });
  