import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InferenceUiDoppl } from './inference-ui-doppl';

describe('InferenceUiDoppl', () => {
  let component: InferenceUiDoppl;
  let fixture: ComponentFixture<InferenceUiDoppl>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InferenceUiDoppl]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InferenceUiDoppl);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
