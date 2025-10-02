import React from 'react';

interface ImageGalleryProps {
  images: string[];
}

const ImageGallery: React.FC<ImageGalleryProps> = ({ images }) => {
  return (
    <div>
      <h2>Image Gallery Component</h2>
      <div className="flex space-x-2">
        {images.map((image, index) => (
          <img key={index} src={image} alt={`Gallery image ${index + 1}`} className="w-24 h-24 object-cover" />
        ))}
      </div>
    </div>
  );
};

export default ImageGallery;