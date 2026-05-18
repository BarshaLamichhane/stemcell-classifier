import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InferenceUiCorintis } from './inference-ui-corintis';

describe('InferenceUiCorintis', () => {
  let component: InferenceUiCorintis;
  let fixture: ComponentFixture<InferenceUiCorintis>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InferenceUiCorintis]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InferenceUiCorintis);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
