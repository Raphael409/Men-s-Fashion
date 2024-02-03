const slideshowImages = document.querySelectorAll(".slideshow-image");
let currentImageIndex = 0;

// Show the first image
slideshowImages[currentImageIndex].classList.add("active");

// Move to the next image every 5 seconds
setInterval(() => {
    slideshowImages[currentImageIndex].classList.remove("active");
    currentImageIndex = (currentImageIndex + 1) % slideshowImages.length;
    slideshowImages[currentImageIndex].classList.add("active");
}, 5000);
