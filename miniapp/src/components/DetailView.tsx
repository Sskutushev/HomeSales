import React from 'react';

interface ListingDetailProps {
  listing: {
    id: string;
    complex_name: string;
    district: string;
    rooms: number;
    area: number;
    price: number;
    price_per_sqm: number;
    images: string[];
    preview_image: string;
    description: string;
  };
}

const DetailView: React.FC<ListingDetailProps> = ({ listing }) => {
  return (
    <div className="mt-6 p-4 border rounded-lg shadow-md">
      <h2 className="text-2xl font-semibold mb-4">Детали объявления</h2>
      <p><strong>Название ЖК:</strong> {listing.complex_name}</p>
      <p><strong>Район:</strong> {listing.district}</p>
      <p><strong>Комнат:</strong> {listing.rooms}</p>
      <p><strong>Площадь:</strong> {listing.area} м²</p>
      <p><strong>Цена:</strong> {listing.price.toLocaleString()} ₽</p>
      <p><strong>Цена за м²:</strong> {listing.price_per_sqm.toLocaleString()} ₽</p>
      <p className="mt-4"><strong>Описание:</strong> {listing.description}</p>
    </div>
  );
};

export default DetailView;
