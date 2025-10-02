import React from 'react';

interface ListingCardProps {
  id: string;
  complexName: string;
  district: string;
  rooms: number;
  area: number;
  price: number;
  previewImage: string;
}

const ListingCard: React.FC<ListingCardProps> = ({
  id,
  complexName,
  district,
  rooms,
  area,
  price,
  previewImage,
}) => {
  return (
    <div className="border p-4 rounded-lg shadow-md">
      <img src={previewImage} alt={complexName} className="w-full h-48 object-cover rounded-md mb-4" />
      <h3 className="text-xl font-semibold mb-2">{complexName}</h3>
      <p className="text-gray-600">Район: {district}</p>
      <p className="text-gray-600">Комнат: {rooms}</p>
      <p className="text-gray-600">Площадь: {area} м²</p>
      <p className="text-lg font-bold mt-2">Цена: {price.toLocaleString()} ₽</p>
      <a href={`/listing/${id}`} className="text-blue-500 hover:underline mt-4 inline-block">Подробнее</a>
    </div>
  );
};

export default ListingCard;