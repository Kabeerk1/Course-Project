function getRecommendations() {
    const movieName = document.getElementById('movieInput').value;
    const recommendationsDiv = document.getElementById('recommendations');

    recommendationsDiv.innerHTML = "Loading...";

    fetch('/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ movie_name: movieName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            recommendationsDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
        } else {
            let html = '<h2>Recommended Movies:</h2><ul>';
            data.recommendations.forEach(movie => {
                html += `
                    <li>
                        <div class="movie-info">
                            <strong>${movie.title} (${movie.release_year || 'N/A'})</strong>
                            <em>Genre: ${movie.genres}</em>
                            <div class="cast">Cast: ${movie.cast || 'N/A'}</div>
                        </div>
                        <div class="description">
                            ${movie.description || 'No description available.'}
                        </div>
                    </li>
                `;
            });
            html += '</ul>';
            recommendationsDiv.innerHTML = html;
        }
    })
    .catch(error => {
        recommendationsDiv.innerHTML = `<p style="color:red;">Something went wrong!</p>`;
    });
}
