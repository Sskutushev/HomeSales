import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';
import DetailView from '../components/DetailView';
import ImageGallery from '../components/ImageGallery';

interface ListingDetail {
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
}

const Listing: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  console.log('Listing ID from useParams:', id);
  const [listing, setListing] = useState<ListingDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchListing = async () => {
      if (!id) {
        setError('Listing ID is missing.');
        setLoading(false);
        return;
      }
      try {
        const response = await apiClient.get<ListingDetail>(`/listings/${id}`);
        setListing(response.data);
      } catch (err) {
        setError('Failed to fetch listing details.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchListing();
  }, [id]);

  if (loading) {
    return <div>Loading listing details...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!listing) {
    return <div>Listing not found.</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">{listing.complex_name}</h1>
      <ImageGallery images={listing.images} />
      <DetailView listing={listing} />
    </div>
  );
};

export default Listing;
