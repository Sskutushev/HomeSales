import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import ListingCard from '../components/ListingCard';

interface Listing {
  id: string;
  complex_name: string;
  district: string;
  rooms: number;
  area: number;
  price: number;
  price_per_sqm: number;
  images: string[];
  preview_image: string;
  description?: string;
}

const Home: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchListings = async () => {
      try {
        const response = await apiClient.get<Listing[]>('/listings');
        setListings(response.data);
      } catch (err) {
        setError('Failed to fetch listings.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchListings();
  }, []);

  if (loading) {
    return <div>Loading listings...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Available Listings</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {listings.map((listing) => (
          <ListingCard
            key={listing.id}
            id={listing.id}
            complexName={listing.complex_name}
            district={listing.district}
            rooms={listing.rooms}
            area={listing.area}
            price={listing.price}
            previewImage={listing.preview_image}
          />
        ))}
      </div>
    </div>
  );
};

export default Home;