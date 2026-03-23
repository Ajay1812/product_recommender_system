const form = document.getElementById("occasion-form");
const input = document.getElementById("occasion-input");
const statusMessage = document.getElementById("status-message");
const resultsGrid = document.getElementById("results-grid");
const resultsTitle = document.getElementById("results-title");
const resultsMeta = document.getElementById("results-meta");
const template = document.getElementById("product-card-template");

function renderResults(occasion, results) {
  resultsGrid.innerHTML = "";

  if (!results.length) {
    resultsTitle.textContent = "No matching products found";
    resultsMeta.textContent = `No products crossed the relevance threshold for "${occasion}".`;
    statusMessage.textContent =
      "Try a broader occasion such as Birthday, Housewarming, or Festival Gift.";
    statusMessage.hidden = false;
    return;
  }

  statusMessage.hidden = true;
  resultsTitle.textContent = `Top recommendations for "${occasion}"`;
  resultsMeta.textContent = `${results.length} ranked products returned below the input field.`;

  results.forEach((product) => {
    const node = template.content.firstElementChild.cloneNode(true);
    const image = node.querySelector(".product-image");
    image.src = product.image_url;
    image.alt = product.title;
    node.querySelector(".category-pill").textContent = product.vendor_category_desc;
    node.querySelector(".score-pill").textContent = `Score ${product.score.toFixed(2)}`;
    node.querySelector(".product-title").textContent = product.title;
    node.querySelector(".product-brand").textContent = product.brand || "Catalog Item";
    node.querySelector(".product-description").textContent = product.description_snippet;
    resultsGrid.appendChild(node);
  });
}

async function searchOccasion(occasion) {
  const trimmed = occasion.trim();
  if (!trimmed) {
    statusMessage.hidden = false;
    statusMessage.textContent = "Enter an occasion before running the search.";
    resultsGrid.innerHTML = "";
    resultsTitle.textContent = "Products will appear below";
    resultsMeta.textContent = "Use a common event or a custom occasion.";
    return;
  }

  statusMessage.hidden = false;
  statusMessage.textContent = `Searching the catalog for "${trimmed}"...`;
  resultsGrid.innerHTML = "";

  try {
    const response = await fetch(`/api/recommend?occasion=${encodeURIComponent(trimmed)}`);
    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }
    const payload = await response.json();
    renderResults(trimmed, payload.results || []);
  } catch (error) {
    statusMessage.hidden = false;
    statusMessage.textContent = "The recommender could not be reached. Check the app server and try again.";
    resultsTitle.textContent = "Search failed";
    resultsMeta.textContent = String(error);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  searchOccasion(input.value);
});

document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    input.value = chip.dataset.occasion;
    searchOccasion(chip.dataset.occasion);
  });
});
