import { Injectable } from '@angular/core';
import { Product } from '../models/product';

@Injectable({ providedIn: 'root' })
export class CartService {
  private items: Product[] = [];

  getItems(): Product[] {
    return [...this.items];
  }

  add(product: Product): void {
    this.items.push(product);
  }

  clear(): void {
    this.items = [];
  }
}
